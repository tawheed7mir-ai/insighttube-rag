# Signal — YouTube Podcast RAG

A portfolio-ready AI project that ingests a YouTube transcript, indexes the content, and answers questions using grounded retrieval and generation.

## Why this structure works

This repo keeps the project separated into the parts that matter for a professional GitHub portfolio and Streamlit deployment:

- `backend/` holds the API entrypoint
- `frontend/` holds the Streamlit UI
- `app/` contains the real retrieval, indexing, generation, and ingestion logic
- `data/` is used for local indexes and cached sources

This keeps the code clean without losing the actual functionality.

## Project structure

```text
langchain.tutor/
├── backend/
│   ├── __init__.py
│   └── app.py
├── frontend/
│   └── streamlit_app.py
├── app/
│   ├── api/
│   ├── core/
│   ├── generation/
│   ├── indexing/
│   ├── ingestion/
│   ├── retrieval/
│   ├── services/
│   └── domain.py
├── data/
├── .streamlit/
│   └── config.toml
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── pyproject.toml
├── requirements.txt
├── README.md
└── tests/
```

## Local setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Add your API key in `.env` if you are using the external model provider.

## Run locally

Open two terminals:

```powershell
# Terminal 1: backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.api.main:app --reload
```

```powershell
# Terminal 2: frontend
.\.venv\Scripts\Activate.ps1
streamlit run frontend\streamlit_app.py
```

Then open:

- Frontend: http://localhost:8501
- API docs: http://localhost:8000/docs

## Deploy to Streamlit Cloud

1. Push the repo to GitHub.
2. In Streamlit Cloud, click New app.
3. Choose the GitHub repo.
4. Set the main file to `frontend/streamlit_app.py`.
5. Add environment variables such as `API_URL` if your backend is hosted elsewhere.

If you want a fully cloud-hosted version, deploy the FastAPI backend separately on Render, Railway, or Hugging Face Spaces and point the frontend to that URL with `API_URL`.

## Deploy both services on Render

This repository includes `render.yaml` for a Render Blueprint with two web services:

1. Create a new Blueprint in Render and select this GitHub repository.
2. Render will create `signal-api` and `signal-frontend` from `render.yaml`.
3. Set `GROQ_API_KEY` and `APP_API_KEY` on the API service. Keep `APP_API_KEY` empty if authentication is not enabled.
4. If you rename the API service, update `API_URL` on the frontend to `https://<your-api-service>.onrender.com`.

The API health check is available at `https://<your-api-service>.onrender.com/health`. The frontend must use the public HTTPS API URL; the local Compose hostname `http://api:8000` only works inside Docker Compose.

Render's local filesystem is ephemeral, so newly ingested transcripts and indexes can be lost after a redeploy or restart. Use a persistent disk or external database/object storage for production data.

## Resume-ready summary

This project demonstrates:

- RAG pipeline design
- document ingestion and chunking
- embedding-based retrieval
- hybrid search and reranking
- grounded answer generation
- Streamlit frontend + FastAPI backend separation
- GitHub deployment readiness

## Project assumptions

This app is designed for a demo/resume portfolio. It is intentionally kept lean and production-friendly for easier deployment and explanation during interviews or job applications.
