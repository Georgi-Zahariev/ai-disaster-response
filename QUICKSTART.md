# Quick Start Guide

Use this guide to run the current backend and frontend stack locally.

## Prerequisites

- Python 3.11+
- Node.js 18+
- pip and npm

## 1. Backend Setup

```bash
cd ai-disaster-response
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set at least one LLM key in `.env` if you want LLM-backed flows:

```bash
OPENAI_API_KEY=sk-...
# or
ANTHROPIC_API_KEY=...
```

## 2. Start Backend

```bash
python backend/main.py
```

Backend endpoints:
- API root: http://localhost:8000/
- Health: http://localhost:8000/health
- Docs: http://localhost:8000/api/docs

## 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend:
- http://localhost:3000

## 4. Run Tests

From repository root:

```bash
pytest
```

Optional focused runs:

```bash
python test_providers.py
python test_incident_endpoint.py
```

## Data Source Notes

- Frontend runtime mode is API-connected by default.
- Backend includes both deterministic providers and live adapters.
- Mock fixture data exists for isolated UI/test usage only.

## Common Issues

- Import errors: ensure commands run from repository root and venv is activated.
- API key errors: verify `.env` has at least one valid LLM key.
- Frontend cannot reach backend: confirm backend is running on port 8000.

Last Updated: March 31, 2026
