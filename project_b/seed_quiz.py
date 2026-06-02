import argparse

from app import create_app
from db import db
from models import (
    Genre,
    QuizAnswerOption,
    QuizAnswerOptionGenre,
    QuizAttempt,
    QuizQuestion,
    QuizResponse,
)


QUIZ_DATA = [
    {
        "question": "What kind of mood are you in?",
        "options": [
            ("Something funny", ["Comedy"]),
            ("Something exciting", ["Action", "Adventure", "Thriller"]),
            ("Something emotional", ["Drama", "Romance"]),
            ("Something scary", ["Horror", "Thriller"]),
        ],
    },
    {
        "question": "How much time do you have?",
        "options": [
            ("A short, easy watch", ["Comedy", "Animation", "Family"]),
            ("A normal movie night", ["Drama", "Adventure", "Mystery"]),
            ("I am ready for something bigger", ["Biography", "History", "War"]),
        ],
    },
    {
        "question": "What kind of story do you want?",
        "options": [
            ("A mystery to solve", ["Mystery", "Crime", "Thriller"]),
            ("A real person or event", ["Biography", "History", "Documentary"]),
            ("A big journey", ["Adventure", "Action", "Fantasy"]),
            ("Music, performance, or sports", ["Music", "Musical", "Sport"]),
        ],
    },
    {
        "question": "Do you want something realistic or imaginative?",
        "options": [
            ("Realistic", ["Drama", "Crime", "Documentary", "Biography"]),
            ("Imaginative", ["Fantasy", "Sci-Fi", "Animation"]),
            ("Somewhere in between", ["Adventure", "Mystery", "Romance"]),
        ],
    },
    {
        "question": "Do you want something light or intense?",
        "options": [
            ("Light", ["Comedy", "Family", "Romance"]),
            ("Intense", ["Thriller", "Horror", "War"]),
            ("Thoughtful", ["Drama", "Film-Noir", "History"]),
        ],
    },
]


def clear_existing_quiz():
    QuizResponse.query.delete()
    QuizAttempt.query.delete()
    QuizAnswerOptionGenre.query.delete()
    QuizAnswerOption.query.delete()
    QuizQuestion.query.delete()
    db.session.commit()


def seed_quiz_data(reset=False):
    if reset:
        clear_existing_quiz()
    elif QuizQuestion.query.first() is not None:
        print("Quiz questions already exist. Use --reset to replace them.")
        return

    genres_by_name = {genre.name: genre for genre in Genre.query.all()}
    if not genres_by_name:
        raise RuntimeError("No genres found. Import the CSV data before seeding the quiz.")

    missing_genres = set()

    for question_index, question_data in enumerate(QUIZ_DATA, start=1):
        question = QuizQuestion(
            question_text=question_data["question"],
            sort_order=question_index,
        )
        db.session.add(question)
        db.session.flush()

        for option_index, (option_text, genre_names) in enumerate(question_data["options"], start=1):
            option = QuizAnswerOption(
                question_id=question.id,
                option_text=option_text,
                sort_order=option_index,
            )
            db.session.add(option)
            db.session.flush()

            for genre_name in genre_names:
                genre = genres_by_name.get(genre_name)
                if genre is None:
                    missing_genres.add(genre_name)
                    continue
                db.session.add(
                    QuizAnswerOptionGenre(
                        quiz_answer_option_id=option.id,
                        genre_id=genre.id,
                    )
                )

    db.session.commit()
    print("Quiz seed data inserted.")
    if missing_genres:
        print("Skipped missing genres: " + ", ".join(sorted(missing_genres)))


def main():
    parser = argparse.ArgumentParser(description="Seed quiz questions and answer options.")
    parser.add_argument("--reset", action="store_true", help="Replace existing quiz data.")
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        db.create_all()
        seed_quiz_data(reset=args.reset)


if __name__ == "__main__":
    main()