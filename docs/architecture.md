# Architecture Overview

## Backend (FastAPI)

- Organized as a modular FastAPI application inside `backend/app`.
- Configuration handled via Pydantic `Settings` sourced from `.env`.
- Supabase client created in `app/supabase.py` for data persistence.
- LLM provider abstraction in `app/services/llm.py` supports OpenAI now and Hugging Face later.

## Frontend (React TBD)

- Placeholder directory `frontend/` ready for either React + Vite or Next.js.
- Once selected, scaffold within this directory and integrate with backend API.

## Data Layer (Supabase)

- Supabase keys loaded from environment variables.
- Extend data access layers or repositories using the shared Supabase client.

## LLM

- `LLMRequest` / `LLMResponse` schema defines API contract.
- `get_llm_client` factory returns provider-specific client at runtime.
- Add caching, rate-limiting, or prompt templates in the `services` layer as the project grows.
