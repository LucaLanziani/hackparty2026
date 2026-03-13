# Backend - Ticket Text Classification API

Flask REST API for the ticket text classification system.

## Setup

### Prerequisites

- Python 3.13+
- PostgreSQL 14+

### Installation

1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up PostgreSQL database:
```bash
# Start PostgreSQL (if using Homebrew on macOS)
#or
docker exec -ti tickets_postgres /bin/bash
su - postgres
# Create database ()
createdb ticket_classification
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run database migrations:
```bash
flask db init
flask db migrate -m "Description of changes"
flask db upgrade
```

## Development

Start the development server:
```bash
flask run
```

The API will be available at `http://localhost:5000`

## Database Migrations

Generate a new migration after model changes:
```bash
flask db migrate -m "Description of changes"
```

Apply migrations:
```bash
flask db upgrade
```

Rollback last migration:
```bash
flask db downgrade
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   └── ticket.py        # Ticket model
│   ├── routes/              # Flask blueprints (API endpoints)
│   └── services/            # Business logic
├── migrations/              # Database migrations (auto-generated)
├── requirements.txt         # Python dependencies
├── run.py                   # Application entry point
└── .env.example            # Environment variables template
```

## Models

### Ticket

Represents a support ticket with classification data.

**Fields:**
- `id` (String, UUID): Primary key
- `text` (Text): Ticket text content (max 5000 chars)
- `category` (String): Classification category (nullable)
- `confidence` (Float): Classification confidence 0-1 (nullable)
- `status` (String): One of 'pending', 'classified', 'failed'
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp

## Testing

Run the Flask shell to test models:
```bash
flask shell
```

Example:
```python
from app.models import Ticket
from app import db

# Create a ticket
ticket = Ticket(text="Test ticket", status="pending")
db.session.add(ticket)
db.session.commit()

# Query tickets
tickets = Ticket.query.all()
```
