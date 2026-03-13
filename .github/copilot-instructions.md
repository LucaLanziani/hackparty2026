# hackparty2026 — Workspace Instructions

## Project Overview

Full-stack web app with:
- **Frontend**: Vite 6 + React 19 + TypeScript + Tailwind CSS v4 + ShadCN UI + React Router v7 (in `frontend/`)
- **Backend**: Python Flask REST API + PostgreSQL (in `backend/`)

## Project Structure

```
hackparty2026/
├── frontend/           # Vite + React + Tailwind boilerplate
│   ├── src/
│   │   ├── components/ # Reusable UI components (ShadCN in ui/)
│   │   ├── pages/      # Route-level page components
│   │   ├── hooks/      # Custom React hooks
│   │   └── lib/        # Utilities and helpers
│   └── package.json
├── backend/            # Flask Python API
│   ├── app/
│   │   ├── __init__.py # App factory (create_app)
│   │   ├── models/     # SQLAlchemy models
│   │   ├── routes/     # Flask blueprints
│   │   └── schemas/    # Serialization schemas
│   ├── migrations/     # Flask-Migrate DB migrations
│   ├── requirements.txt
│   └── run.py
└── .github/
```

## Key Commands

### Frontend (run inside `frontend/`)
```bash
pnpm dev          # Start dev server (http://localhost:5173)
pnpm build        # Production build
pnpm typecheck    # Run TypeScript checks — always run after changes
pnpm lint         # Run ESLint
```

### Backend (run inside `backend/`)
```bash
flask run         # Start dev server (http://localhost:5000)
flask db migrate  # Generate a new DB migration
flask db upgrade  # Apply pending migrations
```

## Frontend ↔ Backend Communication

- Backend API base URL in development: `http://localhost:5000/api`
- Frontend proxies API calls via Vite dev server config or uses `VITE_API_URL` env var
- All API responses are JSON; use `Content-Type: application/json`
- Backend must have CORS enabled for `http://localhost:5173` in development

## General Conventions

- Never commit secrets or `.env` files; use `.env.example` as documentation
- Keep frontend and backend completely decoupled — communicate only via HTTP API
- Use `pnpm` (not npm or yarn) for all frontend package management
- Use `pip` with `requirements.txt` for Python dependencies
