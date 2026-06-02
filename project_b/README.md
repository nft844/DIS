# Movie Match

Movie Match is a local movie recommendation web app.

The user answers a short quiz. The app then recommends movies from the CSV files in this project.

The app uses Flask, PostgreSQL, SQLAlchemy, HTML and CSS.

## What The App Does

1. The user answers quiz questions.
2. Each answer is connected to one or more movie genres.
3. The app finds movies with those genres.
4. The best matches are shown first.

Movies are ranked by:

1. How many selected genres match the movie
2. The movie's average rating
3. The number of votes

## Important Files

```text
app.py              Flask routes
models.py           Database tables
import_data.py      Imports the CSV files
seed_quiz.py        Adds quiz questions and answers
recommendations.py  Recommendation logic
templates/          HTML pages
static/css/         CSS styling
```

## CSV Files

Keep these CSV files in the project folder:

```text
movies.csv
ratings.csv
genres.csv
movie_genres.csv
people.csv
movie_actors.csv
movie_crew.csv
```

## How To Run The Project

Run these commands from the project folder.

### 1. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Start PostgreSQL

If PostgreSQL is not installed on macOS, run:

```bash
brew install postgresql@16
brew services start postgresql@16
```

Create the database:

```bash
/opt/homebrew/opt/postgresql@16/bin/createdb movie_quiz
```

If it says the database already exists, that is okay.

### 3. Create the `.env` file

```bash
cp .env.example .env
```

The default database setting is:

```text
DATABASE_URL=postgresql+psycopg://localhost/movie_quiz
```

### 4. Import the movie data

```bash
python import_data.py --reset
```

This may take a few minutes because the CSV files are large.

### 5. Add the quiz data

```bash
python seed_quiz.py --reset
```

### 6. Run the app

```bash
flask --app app run
```

Open this address in your browser:

```text
http://127.0.0.1:5000
```

## SQL And Regex

The project includes visible SQL statements:

- [app.py](app.py) has `INSERT` statements for saving quiz attempts and answers.
- [recommendations.py](recommendations.py) has a `SELECT` statement for finding recommended movies.

The project also uses regex:

- [recommendations.py](recommendations.py) checks that movie IDs look like IMDb IDs, for example `tt0000009`.

## Notes

- `movies.csv` and `ratings.csv` are combined into one movie table.
- `movie_actors.csv` can contain duplicate rows, so the app gives those rows their own generated ID.
- Some actor or crew rows may reference missing movies or people. Those rows are skipped during import.
- The app is meant to run locally on your computer.
