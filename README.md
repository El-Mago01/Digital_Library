# Digital Library

A small Flask learning project for managing books and authors in a local SQLite database. It supports adding, updating, deleting, listing and searching books and authors, including looking up book and author information through the [Open Library](https://openlibrary.org/) API.

## Getting started

Requires Python 3.12 or newer (the project uses modern Python f-string syntax).

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdir -p data
```

Create a local `.env` file containing a development-only Flask secret key:

```dotenv
SECRET_KEY=replace-with-a-random-local-development-key
```

Initialize the SQLite database once, from the project directory:

```bash
python -c "from app import app; from data_models import db; ctx = app.app_context(); ctx.push(); db.create_all(); ctx.pop()"
```

Then start the application:

```bash
python app.py
```

Open http://127.0.0.1:5003/ in your browser. The application uses `data/library.sqlite` for its local database (ignored by Git). The existing `data/library-old.sqlite` is retained as a historical project file.

## Learning notes (preserved from the original README)

# Digital_Library

Link to exercise: Book Alchemy
https://codio.com/mgorren/book-alchemy
Technology stack:
- API with open library
- First use of flask-sqlalchemy
- Logging
- Hidden HTML form field
- ORM Select query with a join
