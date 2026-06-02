# Movie Match

Movie Match is a local Flask web app that recommends movies from the IMDb CSV files in this folder. The user answers a short quiz, each answer maps to one or more genres, and the app ranks matching movies by genre overlap, rating, and vote count.

The app does not use external movie APIs or machine learning.

## Project Structure

```text
app.py                 Flask routes and app setup
config.py              Environment-based configuration
db.py                  SQLAlchemy database object
models.py              Database tables and relationships
recommendations.py     Quiz-to-movie recommendation logic
import_data.py         CSV import script
seed_quiz.py           Quiz seed script
templates/             Jinja HTML templates
static/css/style.css   App styling
```

The CSV files are expected to stay in the project root by default:

```text
movies.csv
ratings.csv
genres.csv
movie_genres.csv
people.csv
movie_actors.csv
movie_crew.csv
```

## 1. Create and Activate a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Create a PostgreSQL Database

Install and start PostgreSQL if it is not already running.

On macOS with Homebrew:

```bash
brew install postgresql@16
brew services start postgresql@16
```

Homebrew installs PostgreSQL 16 as a versioned package, so the command-line tools may not be on your normal `PATH`. You can either run `createdb` with the full path:

```bash
/opt/homebrew/opt/postgresql@16/bin/createdb movie_quiz
```

Or add PostgreSQL to your shell path and then run `createdb` normally:

```bash
echo 'export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
createdb movie_quiz
```

If `createdb movie_quiz` says the database already exists, you can continue to the next step.

On systems where PostgreSQL is already on your `PATH`, create the local database with:

```bash
createdb movie_quiz
```

If your PostgreSQL setup needs a username, password, host, or port, use a full URL like this instead:

```text
postgresql+psycopg://username:password@localhost:5432/movie_quiz
```

## 3. Configure Environment Variables

Copy the example file and edit it if needed:

```bash
cp .env.example .env
```

Default `.env` values:

```text
DATABASE_URL=postgresql+psycopg://localhost/movie_quiz
SECRET_KEY=change-this-local-secret
CSV_DIR=.
```

`CSV_DIR=.` means the importer will read the CSV files from the project root. If you move the CSV files into another folder, update `CSV_DIR` or pass `--csv-dir` when importing.

## 4. Create Tables and Import CSV Data

From the project root, run:

```bash
python import_data.py --reset
```

This drops and recreates the tables, then imports all seven CSV files. The import prints progress every batch because `movie_actors.csv`, `people.csv`, and `movie_crew.csv` are large.

To import into an already empty database without dropping tables, run:

```bash
python import_data.py
```

If the database already has data, the script stops unless you use `--reset`.

## 5. Seed the Quiz

After importing the CSV data, insert the quiz questions and answer options:

```bash
python seed_quiz.py --reset
```

The seed script uses only genres that exist in the imported `genre` table.

## 6. Run the App

```bash
flask --app app run
```

Open the local URL Flask prints, usually:

```text
http://127.0.0.1:5000
```

## Useful Commands

Create database tables without importing data:

```bash
flask --app app create-db
```

Seed quiz data without replacing existing questions:

```bash
flask --app app seed-quiz
```

Import from a different CSV folder:

```bash
python import_data.py --reset --csv-dir /path/to/csv-folder
```

Use a larger import batch size:

```bash
python import_data.py --reset --batch-size 25000
```

## Recommendation Logic

The recommendation algorithm is intentionally simple:

1. Find the genres connected to the selected quiz answers.
2. Count how many selected genres match each movie.
3. Keep movies with ratings and at least 1,000 votes when possible.
4. Sort by more genre matches, then higher average rating, then more votes.
5. Return about 10 movies.

This keeps the behavior easy to explain while still giving good results from the local dataset.

## SQL and Regex Requirements

The project includes visible SQL statements in the application code:

- [app.py](app.py) uses explicit `INSERT INTO quiz_attempt` and `INSERT INTO quiz_response` statements when saving quiz attempts.
- [recommendations.py](recommendations.py) uses an explicit `SELECT` statement with `JOIN`, `GROUP BY`, and `ORDER BY` to score recommendation matches.

The project also uses regex matching in [recommendations.py](recommendations.py). The `IMDB_MOVIE_ID_RE` pattern validates movie detail URLs so only IMDb-style IDs like `tt0000009` are accepted.

## Notes

- `movie_actors.csv` can contain duplicate rows, so the app imports it into `movie_feature` with a generated numeric primary key.
- Actor and crew rows that reference a missing movie or person are skipped during import and reported in the import output.
- `movies.csv` and `ratings.csv` are combined into one `movie` table. Rating fields are nullable for movies that do not have a rating row.
- The app stores each quiz attempt and response in the database before showing recommendations.
