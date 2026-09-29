# Setup

## Backend

1. Copy `backend/.env.example` to `backend/.env` and set the GitHub webhook secret, GitHub token, Groq API key, and PostgreSQL URL.
2. Install dependencies: `python -m pip install -r backend/requirements.txt`.
3. From `backend/`, start the API: `uvicorn app.main:app --reload`.
4. The API creates missing tables on startup. Its health endpoint is `http://127.0.0.1:8000/health`.

## Frontend

1. Copy `frontend/.env.example` to `frontend/.env.local` and set the GitHub OAuth application credentials and `AUTH_SECRET`.
2. Set the OAuth callback URL to `http://localhost:3000/api/auth/callback/github`.
3. From `frontend/`, run `npm install` and `npm run dev`.

## Docker Compose

Create `backend/.env` from the example first, then run `docker compose -f infrastructure/docker/docker-compose.yml up --build` from the repository root. Compose supplies the internal PostgreSQL URL to the backend.

## Production

Deploy the frontend to Vercel and the backend to Render. Set the same frontend variables in Vercel, using the deployed API URL and production OAuth callback `https://<frontend-domain>/api/auth/callback/github`. Set the backend variables from `backend/.env.example` in Render, use the Render PostgreSQL connection string, and set `CORS_ORIGINS` to the exact deployed frontend origin(s). Configure the GitHub webhook to `https://<backend-domain>/api/v1/webhook` with the same `GITHUB_SECRET` and subscribe to pull request events. To use the manual GitHub Actions deployment workflow, add Vercel and Render deploy hook URLs as repository secrets named `VERCEL_DEPLOY_HOOK_URL` and `RENDER_DEPLOY_HOOK_URL`.

Run backend tests from `backend/` with `python -m pytest app/tests` so the local `.env` is loaded.
