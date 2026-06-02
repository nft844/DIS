from uuid import uuid4

from flask import Flask, abort, redirect, render_template, request, session, url_for
from sqlalchemy import text
from sqlalchemy.orm import selectinload

from config import Config
from db import db
from models import QuizAnswerOption, QuizAttempt, QuizQuestion
from recommendations import get_attempt_summary, get_movie_details, recommend_movies


CREATE_ATTEMPT_SQL = text(
    """
    INSERT INTO quiz_attempt (session_id, created_at)
    VALUES (:session_id, CURRENT_TIMESTAMP)
    RETURNING id
    """
)

SAVE_RESPONSE_SQL = text(
    """
    INSERT INTO quiz_response (quiz_attempt_id, quiz_answer_option_id)
    VALUES (:quiz_attempt_id, :quiz_answer_option_id)
    """
)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/quiz")
    def quiz():
        questions = (
            QuizQuestion.query.options(
                selectinload(QuizQuestion.answer_options).selectinload(QuizAnswerOption.genres)
            )
            .order_by(QuizQuestion.sort_order)
            .all()
        )
        return render_template("quiz.html", questions=questions, error=None)

    @app.post("/quiz")
    def submit_quiz():
        questions = QuizQuestion.query.order_by(QuizQuestion.sort_order).all()
        selected_option_ids = []

        for question in questions:
            selected_value = request.form.get(f"question_{question.id}")
            if selected_value:
                selected_option_ids.append(int(selected_value))

        if questions and len(selected_option_ids) != len(questions):
            questions_with_options = (
                QuizQuestion.query.options(
                    selectinload(QuizQuestion.answer_options).selectinload(QuizAnswerOption.genres)
                )
                .order_by(QuizQuestion.sort_order)
                .all()
            )
            return render_template(
                "quiz.html",
                questions=questions_with_options,
                error="Please answer every question before getting recommendations.",
            ), 400

        if "session_id" not in session:
            session["session_id"] = uuid4().hex

        attempt_id = db.session.execute(
            CREATE_ATTEMPT_SQL,
            {"session_id": session["session_id"]},
        ).scalar_one()

        response_rows = [
            {
                "quiz_attempt_id": attempt_id,
                "quiz_answer_option_id": option_id,
            }
            for option_id in selected_option_ids
        ]
        if response_rows:
            db.session.execute(SAVE_RESPONSE_SQL, response_rows)

        db.session.commit()
        return redirect(url_for("results", attempt_id=attempt_id))

    @app.get("/results/<int:attempt_id>")
    def results(attempt_id):
        attempt = db.session.get(QuizAttempt, attempt_id)
        if attempt is None:
            abort(404)

        summary = get_attempt_summary(attempt_id)
        recommendations = recommend_movies(attempt_id)
        return render_template(
            "results.html",
            attempt=attempt,
            summary=summary,
            recommendations=recommendations,
        )

    @app.get("/movie/<movie_id>")
    def movie_detail(movie_id):
        details = get_movie_details(movie_id)
        if details is None:
            abort(404)
        return render_template("movie_detail.html", **details)

    @app.cli.command("create-db")
    def create_db_command():
        db.create_all()
        print("Database tables created.")

    @app.cli.command("seed-quiz")
    def seed_quiz_command():
        from seed_quiz import seed_quiz_data

        seed_quiz_data(reset=False)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)