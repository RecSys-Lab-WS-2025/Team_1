# Rec Lab Scaffold

This repository provides a starter scaffold for the Rec Lab project across backend, frontend, and LLM integrations.

## Structure

- `backend/`: FastAPI application configured for Supabase and LLM integrations.
- `frontend/`: Placeholder for future React or Next.js application.
- `docs/`: Documentation and design notes.
- `scripts/`: Utility scripts for local development and automation.

## Backend Setup

The backend uses [FastAPI](https://fastapi.tiangolo.com/) with Poetry for dependency management.

### Prerequisites

- Python 3.11+
- [Poetry](https://python-poetry.org/)

### Installation

```bash
cd backend
poetry install
```

### Running the API

```bash
cd backend
poetry run uvicorn app.main:app --reload --port 8000
```

### Environment Variables

Create a `.env` file in `backend/` with the following keys:

```
SUPABASE_URL=<your-supabase-url>
SUPABASE_ANON_KEY=<your-supabase-anon-key>
# Optional service role key if you need elevated privileges:
# SUPABASE_SERVICE_ROLE_KEY=<your-supabase-service-role-key>

LLM_PROVIDER=openai  # or huggingface
OPENAI_API_KEY=<your-openai-api-key>
# Alternatively, when using Hugging Face:
# HUGGINGFACE_API_KEY=<your-huggingface-api-key>
```

## Frontend Placeholder

The frontend stack is yet to be finalized. Use the `frontend/` directory to experiment with React or Next.js. Add a framework-specific README or setup script once the choice is confirmed.

## LLM Integration

The backend includes a service layer (`app/services/llm.py`) that can switch between OpenAI and Hugging Face providers. The OpenAI client is wired up; the Hugging Face implementation contains a placeholder to be completed when the API contract is known.

## Supabase Integration

Supabase is configured through environment variables and exposed via `app/supabase.py`. Inject the Supabase client into routers or services as needed.

## Development Workflow

1. Configure environment variables in `backend/.env`.
2. Install dependencies with Poetry.
3. Run `uvicorn` to start the API server.
4. Add frontend implementation under `frontend/`.
5. Extend the LLM service layer as requirements solidify.
