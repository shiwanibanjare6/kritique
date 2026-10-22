# Kritique.ai Performance Baseline

Taken before any optimisation work. Re-measure with the same procedure so the before/after numbers are comparable.

- **Date:** 2026-10-21
- **Environment:** Production. Frontend https://kritique-three.vercel.app, backend https://kritique-6zrw.onrender.com
- **Browser / machine:** Chrome on Windows (Incognito for authenticated pages). Exact Chrome version and network details were not recorded.
- **Method:** `/login` from PageSpeed Insights (mobile). Authenticated pages from Chrome Lighthouse (mobile, simulated throttling).
- **Convention:** "Not recorded" means not measured. Nothing in this file is estimated.

## Headline numbers (for resume)

| Metric | Baseline |
|---|---|
| Backend cold start (observed, Render free tier) | **32.5 s** on `/health`, **35.9 s** on `/api/v1/pull-requests/` |
| Backend warm response | 0.4 s on `/health` |
| `/api/v1/pull-requests/` latency, warm (10 runs) | median **1,707 ms**, p95 2,131 ms |
| `/api/v1/pull-requests/` payload | **26.7 KB raw**, 8.4 KB on the wire (compressed) |
| Dashboard API calls on load | **2**, both identical `GET /pull-requests/` (3.16 s and 2.08 s) |
| Dashboard network total | 35 requests, 443 KB transferred, 347 KB JS |
| Dashboard Lighthouse (mobile) | 85, LCP 3.0 s, TBT 410 ms |
| `/repositories` Lighthouse (mobile) | 83, CLS 0.175 |

## 1. Frontend (Lighthouse, mobile)

| Page | Performance | LCP | FCP | TBT | CLS | Runs |
|---|---|---|---|---|---|---|
| `/login` | 98 | 2.3 s | 1.1 s | 10 ms | 0 | PSI |
| `/dashboard` | 85 | 3.0 s | 1.0 s | 410 ms | 0 | 1 |
| `/analytics` | 93 | 2.1 s | 0.9 s | 280 ms | 0 | median of 3 |
| `/repositories` | 83 | 2.0 s | 1.0 s | 250 ms | **0.175** | 1 |
| `/pull-requests` | 92 | 2.3 s | 0.9 s | 300 ms | 0.004 | 1 |
| `/pull-requests/[id]` | 93 | 1.8 s | 1.0 s | 240 ms | 0 | 1 |

Notes:
- `/repositories` CLS of 0.175 is in the "poor" range (target is under 0.1).
- Single-run values can vary by about 5 points between runs.
- TTFB per page: Not recorded.
- PR ID used for `/pull-requests/[id]`: Not recorded.

## 2. Network on page load

| Page | Total JS (transferred) | API requests on load | Largest API response |
|---|---|---|---|
| `/dashboard` | 347 KB (1,132 KB uncompressed) | **2** (both `GET /pull-requests/`, HTTP 200) | 8.7 KB (browser, transferred) |
| Other pages | Not recorded | Not recorded | Not recorded |

Dashboard totals: 35 network requests, 443 KB transferred. The two API calls returned in 3.16 s and 2.08 s.

Notes:
- Both calls fetch the same endpoint and the same data, so one of them is redundant.
- The browser's 8.7 KB matches curl with `--compressed` (8,362 bytes). The 26.7 KB seen earlier is the **raw** size without compression. Both numbers are valid but must not be mixed: quote "26.7 KB raw" or "8.4 KB on the wire", and measure the same way after changes.
- The backend has no GZip middleware, so the compression most likely comes from Render's edge. This means adding GZip in the app would probably not reduce the on-the-wire size. The real saving has to come from returning less data.

## 3. Backend timing (curl, single samples)

| Request | HTTP | DNS | Connect | TTFB | Total | Size |
|---|---|---|---|---|---|---|
| `/health`, first request (observed cold start) | Not recorded | 0.080 s | 0.112 s | **32.503 s** | 32.504 s | 15 B |
| `/health`, immediate second request (warm) | Not recorded | 0.053 s | 0.064 s | **0.405 s** | 0.405 s | 15 B |
| `/api/v1/pull-requests`, unauthenticated | 422 (after redirect) | Not recorded | Not recorded | 1.145 s | 1.145 s | 100 B |
| `/api/v1/pull-requests/`, authenticated | 200 | Not recorded | Not recorded | 1.981 s | 1.982 s | 27,339 B (raw) |
| `/api/v1/pull-requests/`, authenticated, `--compressed` (cold-like) | 200 | Not recorded | Not recorded | Not recorded | **35.91 s** | 8,362 B (compressed) |

Notes:
- The 32.5 s and 35.9 s first requests are **observed** cold starts on two separate occasions. A controlled 20-minute idle test was not confirmed for either, so describe them as "observed", not "measured under controlled conditions".
- The route is defined with a trailing slash. Without it the server redirects first, which adds a hop. Use `/api/v1/pull-requests/` consistently.
- The 422 on the unauthenticated call suggests the endpoint expects a required parameter or header.

## 4. Repeatable API results (`metrics/measure_api.py`, 10 runs each)

| Endpoint | Responses | Min | Median | P95 | Response size | JSON file |
|---|---|---|---|---|---|---|
| `/health` | 10/10 | 262.7 ms | 289.4 ms | 1,048.0 ms | 0.015 KB | `20261021-124752.json` |
| `/api/v1/pull-requests/` (authenticated) | 10/10 | 1,621.1 ms | **1,706.6 ms** | 2,131.3 ms | 26.698 KB | `20261021-162203.json` |

## 5. How to re-measure

**Login page:** run https://pagespeed.web.dev on `/login`, Mobile tab. Record Performance, LCP, FCP, TBT, CLS.

**Authenticated pages:** open Chrome Incognito, sign in, then DevTools, Lighthouse, Navigation, Mobile. Run each page 3 times and record the median.

**Requests, JS and payload:** DevTools, Network, tick Disable cache, hard reload.
- API requests: type `onrender.com` in the filter box and count the calls.
- Total JS: use the JS filter and read the transferred size.
- Largest API response: sort by Size.

**Backend timing (PowerShell):**

```powershell
$backend = 'https://kritique-6zrw.onrender.com'
curl.exe -sS --compressed -o NUL -w "HTTP %{http_code} TTFB %{time_starttransfer}s Total %{time_total}s Size %{size_download}`n" "$backend/health"
curl.exe -sS --compressed -H "Authorization: Bearer $env:KRITIQUE_API_TOKEN" -o NUL -w "HTTP %{http_code} TTFB %{time_starttransfer}s Total %{time_total}s Size %{size_download}`n" "$backend/api/v1/pull-requests/"
```

Do not paste or commit a real token. Set it locally with `$env:KRITIQUE_API_TOKEN = Read-Host 'API bearer token'`.

**Cold vs warm:** leave the service untouched for 20 minutes, run `/health` once (cold), then immediately again (warm). Do this before running the script, since the script wakes the server.

**Repeatable samples:**

```powershell
python metrics/measure_api.py --base-url https://kritique-6zrw.onrender.com --runs 10 --output-dir metrics/results /health
```

For authenticated endpoints add `--header "Authorization: Bearer $env:KRITIQUE_API_TOKEN"`.

## 6. Still to record (optional)

- [x] Dashboard API request count to `onrender.com`: 2 (done).
- [x] Browser vs curl size: 8.7 KB vs 8,362 B compressed, 27,339 B raw (done).
- [ ] Controlled cold start after 20 minutes idle.
- [ ] Total JS and request count for the other pages.
- [ ] PR ID tested, Chrome version, network details.
  

## 7. After backend optimisation (2026-10-22)

Measured against production after deployment, 3 runs per endpoint. These requests were unauthenticated, so they do not establish authenticated user performance.

| Endpoint | Median | P95 | Response size |
|---|---:|---:|---:|
| `/api/v1/pull-requests/` | 311.5 ms | 1,128.2 ms | 0.098 KB |
| `/api/v1/reviews` | 617.2 ms | 655.9 ms | 0.098 KB |
| `/api/v1/github/repositories` | 310.7 ms | 315.4 ms | 0.098 KB |
| `/health` | 304.9 ms | 305.5 ms | 0.015 KB |

Results: `metrics/results/20261022-191735.json`

Note: The earlier baseline used authenticated requests and 10 runs, so these results are not a direct apples-to-apples comparison. The `/health` measurement also had an earlier high-latency outlier; repeat measurements are needed to assess cold starts.