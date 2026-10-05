# Kritique.ai

> AI-powered GitHub Pull Request Review Platform

Kritique.ai is a full-stack platform that connects with GitHub repositories and automatically analyzes pull requests across **Security, Style, and Architecture**. It provides structured code-review results through a centralized dashboard with scores, risk assessment, file-level comments, strengths, weaknesses, and review analytics.

---

## 🚀 Live Demo

**Frontend:**  
https://kritique-three.vercel.app

**Backend API:**  
https://kritique-6zrw.onrender.com

**GitHub Repository:**  
https://github.com/shiwanibanjare6/kritique

---

## ✨ Features

### 🔐 GitHub Authentication

- Sign in using your GitHub account.
- Secure authentication using Auth.js / NextAuth.
- GitHub account information is used to access repositories and pull requests.
- Protected application routes ensure that dashboard data is accessible only to authenticated users.

---

### 📂 GitHub Repository Integration

Users can connect their GitHub repositories to Kritique.ai.

Functionality includes:

- View GitHub repositories.
- Connect repositories to Kritique.
- View repository details.
- Associate repositories with pull requests.
- Retrieve repository information through the GitHub API.

---

### 🔄 Pull Request Integration

Kritique.ai integrates directly with GitHub Pull Requests.

The platform can:

- Retrieve pull requests.
- Display pull request information.
- Associate pull requests with repositories.
- Retrieve changed files and pull-request information.
- Process pull requests for review.
- Store review results for later access.

---

### 🔔 GitHub Webhooks

GitHub Webhooks allow Kritique.ai to receive events from connected repositories.

The webhook-based architecture allows the application to react when relevant GitHub activity occurs instead of requiring the user to manually submit every pull request.

The general flow is:

```text
GitHub Repository
       │
       ▼
 GitHub Webhook
       │
       ▼
   FastAPI
       │
       ▼
Pull Request Processing
       │
       ▼
   Code Review
       │
       ▼
 PostgreSQL
