from collections import defaultdict
import re

from sqlalchemy import bindparam, text

from db import db
from models import (
    Genre,
    Movie,
    MovieFeature,
    MovieGenre,
    MovieWork,
    Person,
    QuizAnswerOption,
    QuizAnswerOptionGenre,
    QuizResponse,
)


IMDB_MOVIE_ID_RE = re.compile(r"^tt\d{7,}$")

SELECT_RECOMMENDATIONS_SQL = text(
    """
    SELECT
        m.id AS movie_id,
        COUNT(mg.genre_id) AS match_count
    FROM movie AS m
    JOIN movie_genre AS mg ON mg.movie_id = m.id
    WHERE mg.genre_id IN :genre_ids
        AND m.average_rating IS NOT NULL
        AND m.num_votes IS NOT NULL
        AND m.num_votes >= :min_votes
    GROUP BY m.id, m.average_rating, m.num_votes
    ORDER BY
        COUNT(mg.genre_id) DESC,
        m.average_rating DESC,
        m.num_votes DESC
    LIMIT :limit
    """
).bindparams(bindparam("genre_ids", expanding=True))


def is_valid_movie_id(movie_id):
    return bool(IMDB_MOVIE_ID_RE.fullmatch(movie_id or ""))


def get_attempt_summary(attempt_id):
    selected_options = (
        db.session.query(QuizAnswerOption)
        .join(QuizResponse, QuizResponse.quiz_answer_option_id == QuizAnswerOption.id)
        .filter(QuizResponse.quiz_attempt_id == attempt_id)
        .order_by(QuizAnswerOption.question_id, QuizAnswerOption.sort_order)
        .all()
    )

    selected_genres = (
        db.session.query(Genre)
        .join(QuizAnswerOptionGenre, QuizAnswerOptionGenre.genre_id == Genre.id)
        .join(
            QuizResponse,
            QuizResponse.quiz_answer_option_id == QuizAnswerOptionGenre.quiz_answer_option_id,
        )
        .filter(QuizResponse.quiz_attempt_id == attempt_id)
        .distinct()
        .order_by(Genre.name)
        .all()
    )

    return {
        "selected_options": selected_options,
        "selected_genres": selected_genres,
    }


def _selected_genre_ids(attempt_id):
    rows = (
        db.session.query(QuizAnswerOptionGenre.genre_id)
        .join(
            QuizResponse,
            QuizResponse.quiz_answer_option_id == QuizAnswerOptionGenre.quiz_answer_option_id,
        )
        .filter(QuizResponse.quiz_attempt_id == attempt_id)
        .distinct()
        .all()
    )
    return [row.genre_id for row in rows]


def _recommendation_rows(genre_ids, min_votes, limit):
    # The score is intentionally simple for a student project:
    # 1. more quiz genre matches, 2. higher rating, 3. more votes.
    return db.session.execute(
        SELECT_RECOMMENDATIONS_SQL,
        {
            "genre_ids": genre_ids,
            "min_votes": min_votes,
            "limit": limit,
        },
    ).all()


def _movie_matches_from_rows(rows):
    movie_ids = [row.movie_id for row in rows]
    if not movie_ids:
        return []

    movies_by_id = {
        movie.id: movie
        for movie in Movie.query.filter(Movie.id.in_(movie_ids)).all()
    }

    return [
        (movies_by_id[row.movie_id], int(row.match_count))
        for row in rows
        if row.movie_id in movies_by_id
    ]


def recommend_movies(attempt_id, limit=10, min_votes=1000):
    genre_ids = _selected_genre_ids(attempt_id)
    if not genre_ids:
        return []

    rows = _recommendation_rows(genre_ids, min_votes, limit)

    # If the strict vote filter is too narrow for a niche combination, keep the
    # same scoring but lower the threshold so the page still gives useful results.
    if len(rows) < limit:
        existing_ids = {row.movie_id for row in rows}
        fallback_rows = [
            row
            for row in _recommendation_rows(genre_ids, 100, limit + len(existing_ids) + 20)
            if row.movie_id not in existing_ids
        ]
        rows.extend(fallback_rows[: limit - len(rows)])

    movie_matches = _movie_matches_from_rows(rows)
    movie_ids = [movie.id for movie, _match_count in movie_matches]
    genres_by_movie = _genres_for_movies(movie_ids)
    directors_by_movie = _crew_for_movies(movie_ids, "director", limit_per_movie=2)
    actors_by_movie = _actors_for_movies(movie_ids, limit_per_movie=3)

    recommendations = []
    for movie, match_count in movie_matches:
        recommendations.append(
            {
                "movie": movie,
                "match_count": match_count,
                "genres": genres_by_movie.get(movie.id, []),
                "directors": directors_by_movie.get(movie.id, []),
                "actors": actors_by_movie.get(movie.id, []),
            }
        )
    return recommendations


def get_movie_details(movie_id):
    if not is_valid_movie_id(movie_id):
        return None

    movie = db.session.get(Movie, movie_id)
    if movie is None:
        return None

    return {
        "movie": movie,
        "genres": _genres_for_movies([movie_id]).get(movie_id, []),
        "actors": _actors_for_movies([movie_id], limit_per_movie=15).get(movie_id, []),
        "directors": _crew_for_movies([movie_id], "director", limit_per_movie=10).get(movie_id, []),
        "writers": _crew_for_movies([movie_id], "writer", limit_per_movie=10).get(movie_id, []),
    }


def _genres_for_movies(movie_ids):
    result = defaultdict(list)
    if not movie_ids:
        return result

    rows = (
        db.session.query(MovieGenre.movie_id, Genre.name)
        .join(Genre, Genre.id == MovieGenre.genre_id)
        .filter(MovieGenre.movie_id.in_(movie_ids))
        .order_by(MovieGenre.movie_id, Genre.name)
        .all()
    )
    for movie_id, genre_name in rows:
        result[movie_id].append(genre_name)
    return result


def _crew_for_movies(movie_ids, role, limit_per_movie):
    result = defaultdict(list)
    if not movie_ids:
        return result


    rows = (
        db.session.query(MovieWork.movie_id, Person.name)
        .join(Person, Person.id == MovieWork.person_id)
        .filter(MovieWork.movie_id.in_(movie_ids), MovieWork.role == role)
        .order_by(MovieWork.movie_id, MovieWork.id)
        .all()
    )
    for movie_id, person_name in rows:
        if len(result[movie_id]) < limit_per_movie and person_name not in result[movie_id]:
            result[movie_id].append(person_name)
    return result


def _actors_for_movies(movie_ids, limit_per_movie):
    result = defaultdict(list)
    if not movie_ids:
        return result

    rows = (
        db.session.query(MovieFeature.movie_id, Person.name)
        .join(Person, Person.id == MovieFeature.person_id)
        .filter(MovieFeature.movie_id.in_(movie_ids))
        .order_by(MovieFeature.movie_id, MovieFeature.id)
        .all()
    )
    for movie_id, person_name in rows:
        if len(result[movie_id]) < limit_per_movie and person_name not in result[movie_id]:
            result[movie_id].append(person_name)
    return result