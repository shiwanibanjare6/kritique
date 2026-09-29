# API

- `GET /health` is the unauthenticated liveness check.
- Authenticated dashboard, repository, pull request, and review endpoints require `Authorization: Bearer <GitHub OAuth access token>`.
- `GET /api/v1/github/github-repositories` lists repositories available to that GitHub account.
- `POST /api/v1/github/repositories/connect` verifies the selected repository with GitHub and associates it with the signed-in account.
- `POST /api/v1/webhook` receives GitHub pull request events and verifies `X-Hub-Signature-256` using `GITHUB_SECRET`.

Set `NEXT_PUBLIC_API_URL` to the backend origin. Set `CORS_ORIGINS` to comma-separated, exact frontend origins.
