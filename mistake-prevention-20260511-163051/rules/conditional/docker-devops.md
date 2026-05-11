---
paths:
  - "**/Dockerfile"
  - "**/Dockerfile.*"
  - "**/docker-compose*"
  - ".github/**"
  - "**/nginx.conf"
  - "**/infra/**"
---

# Docker & DevOps Rules

## Docker Policy (Non-negotiable)
- All services containerized by default. docker-compose.yml required
- Must include: DB, Backend API, Web frontend (prod), Nginx, infrastructure
- **Exception**: FastAPI serving AI models with Apple Silicon MPS/GPU → runs on host machine (Docker cannot access MPS). Connect via `host.docker.internal`
- devops-engineer handles all Docker configuration
- docker-compose.yml must include dev/prod profiles

## CI/CD
- lint → test → build → deploy pipeline
- Sensitive info (.env, credentials) must NEVER be included
