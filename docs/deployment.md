# Deployment

## Local Docker deployment

Run both services locally:

```powershell
docker compose up --build
```

Open the frontend at `http://localhost:8501`. The Compose-only API hostname is
`http://api:8000`; it must not be used by a separately hosted frontend.

## Render deployment

The repository contains `render.yaml`, which defines two Docker web services:

- `signal-api`: FastAPI at `/health`, `/ingest`, `/query`, and `/videos`
- `signal-frontend`: Streamlit, configured with `API_URL`

### Blueprint setup

1. Push the repository, including `render.yaml`, to GitHub.
2. In Render, select **New > Blueprint** and connect the repository.
3. Apply the Blueprint. Render creates both services.
4. Open the `signal-api` service and add `GROQ_API_KEY` as a secret.
5. Add `APP_API_KEY` only if application authentication is enabled. Otherwise leave it blank.
6. Wait for the API deploy to become healthy, then open:
	`https://signal-api.onrender.com/health`
7. Open the Streamlit service URL.

The frontend's default Render value is:

```text
API_URL=https://signal-api.onrender.com
```

If the API service is renamed, change the frontend `API_URL` to the exact API
service URL, including `https://`, and redeploy the frontend.

### Manual service setup

If a Blueprint is not used, create two **Web Service** entries from the same
repository with Docker selected:

API service:

```text
Dockerfile: ./Dockerfile
Docker command: uvicorn app.api.main:app --host 0.0.0.0 --port $PORT
Health check path: /health
```

Streamlit service:

```text
Dockerfile: ./Dockerfile
Docker command: streamlit run frontend/streamlit_app.py --server.address 0.0.0.0 --server.port $PORT
Environment variable: API_URL=https://<api-service-name>.onrender.com
```

Set these API environment variables in Render:

```text
APP_ENV=production
GROQ_API_KEY=<your Groq key>
APP_API_KEY=<optional application key>
```

YouTube may reject requests from Render datacenter IPs with `403 Forbidden`.
If that happens, add `YOUTUBE_PROXY` to the API service using a trusted
residential or mobile HTTP(S) proxy URL, for example:

```text
YOUTUBE_PROXY=http://username:password@proxy-host:proxy-port
```

Keep this value secret. A normal web proxy or a proxy without YouTube access
will not fix the request. Without a proxy, use a transcript provider API or
upload/paste transcripts instead.

Do not commit `.env` or any API key to GitHub.

### Troubleshooting

- **API offline in Streamlit:** verify the frontend `API_URL` is the public API URL, not `http://localhost:8000` or `http://api:8000`.
- **API deploy fails health check:** confirm the command uses `--host 0.0.0.0 --port $PORT`.
- **Answers use the fallback generator:** verify `GROQ_API_KEY` is set and the API service has redeployed.
- **First request is slow:** free Render services sleep when idle and may need time to download embedding or reranker models.
- **Indexed videos disappear:** Render's local filesystem is ephemeral. Add a persistent disk or move vector, sparse, and source storage to a managed database/object store for production.


## Production requirements

Before treating this as a production service, add persistent storage, authentication,
rate limiting, request timeouts, background ingestion jobs, secret management,
structured logs, and monitoring. The current JSON indexes are appropriate for a
small demo, not for multiple replicas or durable user data.
