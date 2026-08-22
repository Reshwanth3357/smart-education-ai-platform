# SakshamAI

Runnable competency-intelligence demo for India's Official Statistical System.

Run: `python -m pip install -r requirements.txt` then `python -m uvicorn apps.api.main:app --reload`, and open http://localhost:8000.

Demo accounts: Aarav (employee), Meera (trainer), and Kavita (administrator), all with password `demo123`.

Implemented: backend RBAC, JWT-style development authentication, persistent seeded competency framework (34 competencies), evidence-based assessments, skill-gap calculation, personalised recommendations, iGOT-labelled sandbox course data, document upload validation, generated questions held at `REVIEW_REQUIRED`, and explicit trainer publication gate.

Mock/sandbox data is visibly identified. Production configuration must supply PostgreSQL/pgvector, object storage, background worker/n8n webhooks, document extractors, LLM/RAG provider, and government SSO. No live iGOT or government partnership is claimed.
