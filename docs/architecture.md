# Architecture Overview

## Backend (FastAPI)

- Organized as a modular FastAPI application inside `backend/app`.
- Configuration handled via Pydantic `Settings` sourced from `.env`.
- Database access via SQLAlchemy ORM with async support (`app/database.py`).
- Database models defined in `app/models/` directory.

## Frontend (React TBD)

- Placeholder directory `frontend/` ready for either React + Vite or Next.js.
- Once selected, scaffold within this directory and integrate with backend API.

## Data Layer (SQLAlchemy + SQLite)

- Local SQLite database stored in `backend/data/app.db` by default.
- The path can be overridden via the `DATABASE_URL` environment variable (supports any async SQLAlchemy URL).
- SQLAlchemy async engine and session management live in `app/database.py`.
- Database migrations handled by Alembic.
- Models inherit from `Base` in `app/models/base.py`.
- Database sessions injected via FastAPI dependency injection (`Depends(get_db)`).
- Outdooractive (or other) datasets should be ingested into SQLite via a one-off script or management command before being served by the API.

## Database Migrations

- Alembic configured for database schema versioning.
- Migration files in `alembic/versions/`.
- Run `alembic revision --autogenerate -m "description"` to create migrations.
- Run `alembic upgrade head` to apply migrations.
