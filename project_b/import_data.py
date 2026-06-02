import argparse
import csv
from pathlib import Path

from app import create_app
from config import Config
from db import db
from models import Genre, Movie, MovieFeature, MovieGenre, MovieWork, Person, QuizQuestion


DEFAULT_BATCH_SIZE = 10000


def clean_text(value):
    value = (value or "").strip()
    return value or None


def parse_int(value):
    value = clean_text(value)
    return int(value) if value is not None else None


def parse_float(value):
    value = clean_text(value)
    return float(value) if value is not None else None


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as csv_file:
        yield from csv.DictReader(csv_file)


def insert_batches(model, rows, label, batch_size=DEFAULT_BATCH_SIZE):
    buffer = []
    total = 0

    for row in rows:
        buffer.append(row)
        if len(buffer) >= batch_size:
            db.session.execute(model.__table__.insert(), buffer)
            db.session.commit()
            total += len(buffer)
            print(f"{label}: imported {total:,} rows")
            buffer.clear()

    if buffer:
        db.session.execute(model.__table__.insert(), buffer)
        db.session.commit()
        total += len(buffer)

    print(f"{label}: finished with {total:,} rows")


def existing_ids(model):
    return {row.id for row in db.session.query(model.id).all()}


def load_ratings(csv_dir):
    ratings_path = csv_dir / "ratings.csv"
    ratings = {}
    for row in read_csv(ratings_path):
        ratings[row["movie_id"]] = {
            "average_rating": parse_float(row["average_rating"]),
            "num_votes": parse_int(row["num_votes"]),
        }
    print(f"ratings.csv: loaded {len(ratings):,} ratings into memory")
    return ratings


def import_genres(csv_dir, batch_size):
    rows = (
        {
            "id": parse_int(row["genre_id"]),
            "name": clean_text(row["genre_name"]),
        }
        for row in read_csv(csv_dir / "genres.csv")
    )
    insert_batches(Genre, rows, "genres.csv", batch_size)


def import_people(csv_dir, batch_size):
    rows = (
        {
            "id": clean_text(row["person_id"]),
            "name": clean_text(row["name"]) or "Unknown",
        }
        for row in read_csv(csv_dir / "people.csv")
    )
    insert_batches(Person, rows, "people.csv", batch_size)


def import_movies(csv_dir, batch_size):
    ratings = load_ratings(csv_dir)

    def rows():
        for row in read_csv(csv_dir / "movies.csv"):
            rating = ratings.get(row["movie_id"], {})
            yield {
                "id": clean_text(row["movie_id"]),
                "title": clean_text(row["title"]) or "Untitled",
                "start_year": parse_int(row["start_year"]),
                "runtime_minutes": parse_int(row["runtime_minutes"]),
                "average_rating": rating.get("average_rating"),
                "num_votes": rating.get("num_votes"),
            }

    insert_batches(Movie, rows(), "movies.csv + ratings.csv", batch_size)


def import_movie_genres(csv_dir, batch_size):
    seen_pairs = set()

    def rows():
        for row in read_csv(csv_dir / "movie_genres.csv"):
            movie_id = clean_text(row["movie_id"])
            genre_id = parse_int(row["genre_id"])
            pair = (movie_id, genre_id)
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            yield {
                "movie_id": movie_id,
                "genre_id": genre_id,
            }

    insert_batches(MovieGenre, rows(), "movie_genres.csv", batch_size)


def import_movie_features(csv_dir, batch_size):
    movie_ids = existing_ids(Movie)
    person_ids = existing_ids(Person)
    skipped = 0

    def rows():
        nonlocal skipped
        for row in read_csv(csv_dir / "movie_actors.csv"):
            movie_id = clean_text(row["movie_id"])
            person_id = clean_text(row["person_id"])
            if movie_id not in movie_ids or person_id not in person_ids:
                skipped += 1
                continue
            yield {
                "movie_id": movie_id,
                "person_id": person_id,
                "characters": clean_text(row["characters"]),
            }

    insert_batches(MovieFeature, rows(), "movie_actors.csv", batch_size)
    if skipped:
        print(f"movie_actors.csv: skipped {skipped:,} rows with missing movie/person references")


def import_movie_work(csv_dir, batch_size):
    movie_ids = existing_ids(Movie)
    person_ids = existing_ids(Person)
    skipped = 0

    def rows():
        nonlocal skipped
        for row in read_csv(csv_dir / "movie_crew.csv"):
            movie_id = clean_text(row["movie_id"])
            person_id = clean_text(row["person_id"])
            if movie_id not in movie_ids or person_id not in person_ids:
                skipped += 1
                continue
            yield {
                "movie_id": movie_id,
                "person_id": person_id,
                "role": clean_text(row["role"]),
            }

    insert_batches(MovieWork, rows(), "movie_crew.csv", batch_size)
    if skipped:
        print(f"movie_crew.csv: skipped {skipped:,} rows with missing movie/person references")


def database_has_data():
    return any(
        model.query.first() is not None
        for model in (Movie, Person, Genre, MovieGenre, MovieFeature, MovieWork, QuizQuestion)
    )


def ensure_csv_files_exist(csv_dir):
    required_files = [
        "movies.csv",
        "ratings.csv",
        "genres.csv",
        "movie_genres.csv",
        "people.csv",
        "movie_actors.csv",
        "movie_crew.csv",
    ]
    missing = [filename for filename in required_files if not (csv_dir / filename).exists()]
    if missing:
        missing_list = ", ".join(missing)
        raise FileNotFoundError(f"Missing CSV files in {csv_dir}: {missing_list}")


def import_all(csv_dir, batch_size=DEFAULT_BATCH_SIZE, reset=False):
    csv_dir = Path(csv_dir).resolve()
    ensure_csv_files_exist(csv_dir)

    if reset:
        print("Dropping and recreating database tables...")
        db.drop_all()
        db.create_all()
    else:
        db.create_all()
        if database_has_data():
            raise RuntimeError(
                "The database already has data. Re-run with --reset to rebuild it from the CSV files."
            )

    print(f"Importing CSV files from {csv_dir}")
    import_genres(csv_dir, batch_size)
    import_people(csv_dir, batch_size)
    import_movies(csv_dir, batch_size)
    import_movie_genres(csv_dir, batch_size)
    import_movie_features(csv_dir, batch_size)
    import_movie_work(csv_dir, batch_size)
    print("CSV import complete.")


def main():
    parser = argparse.ArgumentParser(description="Import IMDb CSV files into the local database.")
    parser.add_argument("--csv-dir", default=Config.CSV_DIR, help="Folder containing the CSV files.")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--reset", action="store_true", help="Drop and recreate tables before importing.")
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        import_all(args.csv_dir, batch_size=args.batch_size, reset=args.reset)


if __name__ == "__main__":
    main()