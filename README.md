# PocketSmart AI

A complete FastAPI + Jinja2 GenAI budget and recommendation assistant based on the supplied project specification. It provides Home Interior, Party, and Jewelry planners, user authentication, recommendation history, optional jewelry outfit-image analysis, platform-aware links, and deterministic fallback recommendations when Gemini is unavailable.

## Features
- FastAPI backend with modular routers/services/models.
- Jinja2 responsive frontend.
- JWT authentication with bcrypt password hashing.
- SQLite persistence for users and recommendation history.
- Gemini integration through Google's current `google-genai` SDK.
- Configurable Gemini model via `GEMINI_MODEL`.
- Text and optional image input for Jewelry Planner.
- Budget validation and server-side safety limits.
- Fallback recommendations when no API key is configured or Gemini fails.
- `/docs` OpenAPI documentation.
- Automated API tests.

## Run locally

### 1. Create environment
```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# macOS/Linux
source .venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
copy .env.example .env
```
Add your Gemini API key to `.env`. If you leave it blank, the application still works using built-in fallback recommendations.

### 4. Start
```bash
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000

## API endpoints
- `POST /register`
- `POST /login`
- `POST /token`
- `POST /logout`
- `GET /session-info`
- `GET /session-data`
- `POST /generate-home`
- `POST /generate-party`
- `POST /generate-jewelry`
- `GET /recommendations-details/{recommendation_id}`
- `GET /history`
- `GET /startup`

The planner endpoints require a bearer token. The browser UI stores the token in localStorage and sends it automatically.

## Gemini note
The supplied documentation names Gemini 1.5 Flash Pro. Model availability changes over time, so the implementation keeps the model configurable through `GEMINI_MODEL`; set it to a model enabled for your Google AI account. The code does not hard-code a deprecated endpoint.
