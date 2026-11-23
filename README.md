# SakshamAI

Runnable competency-intelligence demo for India's Official Statistical System.

Run: `python -m pip install -r requirements.txt` then `python -m uvicorn apps.api.main:app --reload`, and open http://localhost:8000.

Demo accounts: Aarav (employee), Meera (trainer), and Kavita (administrator), all with password `demo123`.

Implemented: backend RBAC, JWT-style development authentication, persistent seeded competency framework (34 competencies), evidence-based assessments, skill-gap calculation, personalised recommendations, iGOT-labelled sandbox course data, document upload validation, generated questions held at `REVIEW_REQUIRED`, and explicit trainer publication gate.

Mock/sandbox data is visibly identified. Production configuration must supply PostgreSQL/pgvector, object storage, background worker/n8n webhooks, document extractors, LLM/RAG provider, and government SSO. No live iGOT or government partnership is claimed.
# Smart Education AI Platform

A full-stack educational AI application combining a Python backend API, a web frontend, and automated n8n workflows, packaged with Docker.

## Architecture

![Smart Education AI Platform Architecture](docs/architecture.png)

## Project Structure

```text
smart-education-ai-platform-main/
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md[cite: 11]
├── apps/[cite: 11]
│   ├── api/[cite: 11]
│   │   └── main.py[cite: 11]
│   └── web/[cite: 11]
│       └── public/[cite: 11]
│           ├── index.html[cite: 11]
│           ├── app.js[cite: 11]
│           └── style.css[cite: 11]
└── n8n/[cite: 11]
    └── workflows/[cite: 11]
        └── README.md[cite: 11]
