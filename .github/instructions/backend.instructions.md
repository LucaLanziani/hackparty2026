---
description: "Use when writing backend code: Flask routes, models, schemas, migrations, or database logic. Covers Flask app factory pattern, SQLAlchemy, Flask-Migrate, CORS, and PostgreSQL conventions."
applyTo: "backend/**"
---

# Backend Guidelines

## Stack

- **Flask** — web framework; use app factory pattern (`create_app` in `app/__init__.py`)
- **Flask-SQLAlchemy** — ORM for PostgreSQL
- **Flask-Migrate** — Alembic-based DB migrations
- **Flask-CORS** — enable CORS for `http://localhost:5173` in development
- **psycopg2-binary** — PostgreSQL driver
- **python-dotenv** — load `.env` for local config

## Project Structure

```
backend/
├── app/
│   ├── __init__.py     # create_app() factory
│   ├── models/         # SQLAlchemy model classes
│   ├── routes/         # Flask blueprints (one per resource)
│   └── schemas/        # Serialization (marshmallow or manual dicts)
├── migrations/         # Flask-Migrate generated files — do not hand-edit
├── requirements.txt
├── .env.example        # Document required env vars here
└── run.py              # Entry point: from app import create_app
```

## App Factory Pattern

```python
# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, origins=["http://localhost:5173"])

    from app.routes.example import bp as example_bp
    app.register_blueprint(example_bp, url_prefix="/api/example")

    return app
```

## Models

- One file per model in `app/models/`, import and re-export from `app/models/__init__.py`
- Always define `__tablename__` explicitly (snake_case, plural)
- Include `id`, `created_at`, and `updated_at` on every model

```python
from app import db
from datetime import datetime, timezone

class Item(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
```

## Routes / Blueprints

- One blueprint per resource in `app/routes/`
- All endpoints under `/api/` prefix
- Return JSON with consistent shape: `{"data": ..., "error": null}` on success, `{"data": null, "error": "message"}` on error
- Use appropriate HTTP status codes (200, 201, 400, 404, 500)

```python
from flask import Blueprint, jsonify, request
from app.models import Item
from app import db

bp = Blueprint("items", __name__)

@bp.get("/")
def list_items():
    items = Item.query.all()
    return jsonify({"data": [i.to_dict() for i in items], "error": None})
```

## Migrations

```bash
flask db migrate -m "describe the change"   # generate migration file
flask db upgrade                             # apply to database
flask db downgrade                           # roll back one step
```

Always review the generated migration file before applying it.

## Environment Variables

Required variables (document in `.env.example`, never commit `.env`):

```
FLASK_APP=run.py
FLASK_ENV=development
DATABASE_URL=postgresql://user:password@localhost:5432/hackparty2026
SECRET_KEY=change-me-in-production
```

## Security

- Never expose raw SQLAlchemy errors to the API response
- Validate and sanitize all request inputs before using in queries
- Use parameterized queries (SQLAlchemy ORM does this by default — never use `text()` with raw user input)
- `SECRET_KEY` must be a long random string in production

## Checks

- Run `flask shell` to manually test queries during development
- Confirm models are importable before generating migrations
