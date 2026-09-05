# Deployment, Operations & Production Readiness Guide

## SIH26083 Extreme Heatwave Risk Engine

This guide details local execution, containerization, production deployment, and monitoring.

---

### 1. Local Development Setup

#### Prerequisites
- Python 3.10+ (Python 3.11 recommended)
- `pip` package manager
- `git`

#### Installation Steps
```bash
# 1. Clone repository
git clone https://github.com/fatehbrar07/SIH26083-Heat-Risk.git
cd SIH26083-Heat-Risk

# 2. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment configuration
cp .env.example .env

# 5. Run test suite to verify science and API
PYTHONPATH=. pytest backend/tests/

# 6. Start development server
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
Open your browser at `http://localhost:8000` to access the interactive dashboard or `http://localhost:8000/docs` for the OpenAPI documentation.

---

### 2. Docker & Container Deployment

#### Using Docker Compose (Recommended)
```bash
docker-compose up --build -d
```
Check status:
```bash
docker-compose ps
docker-compose logs -f
```

#### Standalone Docker Run
```bash
docker build -t sih26083-heat-risk:latest .
docker run -d -p 8000:8000 --name sih26083-app sih26083-heat-risk:latest
```

---

### 3. Production Hardening & Observability

- **Reverse Proxy:** Terminate SSL/TLS via Nginx or Caddy on port 443 proxying to `127.0.0.1:8000`.
- **Health Checks:** Monitor `GET /health` with uptime monitors (e.g. Prometheus Blackbox Exporter or BetterStack).
- **Caching:** Weather forecast calls to Open-Meteo are cached in-memory with a configurable 1-hour TTL (`WEATHER_CACHE_TTL=3600`) to adhere to rate-limiting best practices and ensure zero external dependency failure during live presentations.
- **Failover / Offline Demonstration:** Set `DEMO_MODE=true` in `.env` for fully offline, deterministic presentation fallback.
