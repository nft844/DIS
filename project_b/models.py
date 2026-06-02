from datetime import datetime, timezone

from db import db


class Person(db.Model):
    __tablename__ = "person"

    id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(255), nullable=False, index=True)

    features = db.relationship("MovieFeature", back_populates="person")
    works = db.relationship("MovieWork", back_populates="person")


class Movie(db.Model):
    __tablename__ = "movie"

    id = db.Column(db.String(20), primary_key=True)
    title = db.Column(db.Text, nullable=False)
    start_year = db.Column(db.Integer, nullable=True, index=True)
    average_rating = db.Column(db.Float, nullable=True, index=True)
    num_votes = db.Column(db.Integer, nullable=True, index=True)
    runtime_minutes = db.Column(db.Integer, nullable=True)

    genres = db.relationship("Genre", secondary="movie_genre", back_populates="movies")
    features = db.relationship("MovieFeature", back_populates="movie")
    works = db.relationship("MovieWork", back_populates="movie")


class Genre(db.Model):
    __tablename__ = "genre"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)

    movies = db.relationship("Movie", secondary="movie_genre", back_populates="genres")
    quiz_answer_options = db.relationship(
        "QuizAnswerOption",
        secondary="quiz_answer_option_genre",
        back_populates="genres",
    )


class MovieFeature(db.Model):
    __tablename__ = "movie_feature"

    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.String(20), db.ForeignKey("person.id"), nullable=False, index=True)
    movie_id = db.Column(db.String(20), db.ForeignKey("movie.id"), nullable=False, index=True)
    characters = db.Column(db.Text, nullable=True)

    person = db.relationship("Person", back_populates="features")
    movie = db.relationship("Movie", back_populates="features")


class MovieWork(db.Model):
    __tablename__ = "movie_work"

    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.String(20), db.ForeignKey("person.id"), nullable=False, index=True)
    movie_id = db.Column(db.String(20), db.ForeignKey("movie.id"), nullable=False, index=True)
    role = db.Column(db.String(30), nullable=False, index=True)

    person = db.relationship("Person", back_populates="works")
    movie = db.relationship("Movie", back_populates="works")


class MovieGenre(db.Model):
    __tablename__ = "movie_genre"

    movie_id = db.Column(db.String(20), db.ForeignKey("movie.id"), primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"), primary_key=True)


class QuizQuestion(db.Model):
    __tablename__ = "quiz_question"

    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(255), nullable=False)
    sort_order = db.Column(db.Integer, nullable=False, index=True)

    answer_options = db.relationship(
        "QuizAnswerOption",
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="QuizAnswerOption.sort_order",
    )


class QuizAnswerOption(db.Model):
    __tablename__ = "quiz_answer_option"

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("quiz_question.id"), nullable=False, index=True)
    option_text = db.Column(db.String(255), nullable=False)
    sort_order = db.Column(db.Integer, nullable=False, index=True)

    question = db.relationship("QuizQuestion", back_populates="answer_options")
    genres = db.relationship(
        "Genre",
        secondary="quiz_answer_option_genre",
        back_populates="quiz_answer_options",
    )


class QuizAttempt(db.Model):
    __tablename__ = "quiz_attempt"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(64), nullable=False, index=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    responses = db.relationship(
        "QuizResponse",
        back_populates="quiz_attempt",
        cascade="all, delete-orphan",
    )


class QuizResponse(db.Model):
    __tablename__ = "quiz_response"

    id = db.Column(db.Integer, primary_key=True)
    quiz_attempt_id = db.Column(db.Integer, db.ForeignKey("quiz_attempt.id"), nullable=False, index=True)
    quiz_answer_option_id = db.Column(
        db.Integer,
        db.ForeignKey("quiz_answer_option.id"),
        nullable=False,
        index=True,
    )

    quiz_attempt = db.relationship("QuizAttempt", back_populates="responses")
    answer_option = db.relationship("QuizAnswerOption")


class QuizAnswerOptionGenre(db.Model):
    __tablename__ = "quiz_answer_option_genre"

    quiz_answer_option_id = db.Column(
        db.Integer,
        db.ForeignKey("quiz_answer_option.id"),
        primary_key=True,
    )
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"), primary_key=True)