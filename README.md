# Kritique.ai

Kritique.ai connects GitHub repositories, analyzes pull requests with the existing AI review pipeline, and stores review results and score breakdowns in PostgreSQL. GitHub pull-request webhooks enqueue durable review jobs; a separate worker processes them.

## Local development

### Configure the backend

Copy `backend/.env.example` to `backend/.env` and set the required GitHub webhook secret, GitHub API token, and Groq API key. The example uses local PostgreSQL and Redis URLs; do not commit `backend/.env`.

### Start PostgreSQL and Redis

From the repository root:

```bash
docker compose -f infrastructure/docker/docker-compose.yml up -d postgres redis
```

### Start the FastAPI backend

In a terminal:

```bash
cd backend
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API initializes the database schema at startup and is available at `http://127.0.0.1:8000`.

### Start the review worker

In a second backend terminal:

```bash
cd backend
python -m app.workers.review_worker
```

Run one worker process for this local setup. PostgreSQL stores queued job state; Redis wakes the worker quickly. If Redis is unavailable, the worker continues polling queued database jobs.

### Start the Next.js frontend

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend is available at `http://localhost:3000`. Set its Auth.js and GitHub OAuth values in `frontend/.env.local` using `frontend/.env.example` as a reference.

## Review job behavior

The webhook endpoint validates GitHub's HMAC signature, records the delivery and pull-request revision, and returns a queued response without waiting for AI analysis. PostgreSQL uniqueness constraints prevent duplicate deliveries and jobs for the same pull-request head SHA. A later head SHA can create a new review job. Failed jobs are not automatically retried; a later PR revision can create a new job. Automatic retries are intentionally omitted because posting a GitHub review is an external side effect that needs its own idempotency design.

The worker runs the existing `AIReviewService` pipeline, persists the review and changed-file data, posts the result to GitHub, and records `queued`, `processing`, `completed`, or `failed` status. The Pull Requests table and detail page display review status.

## Checks

Frontend checks run from `frontend`:

```bash
npm run lint
npx tsc --noEmit
npm run build
```

Backend tests run from the repository root:

```bash
pytest backend/app/tests
```
