import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://localhost/movie_quiz",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CSV_DIR = Path(os.getenv("CSV_DIR", BASE_DIR)).resolve()