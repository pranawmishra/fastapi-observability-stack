# FastAPI Observability Stack — Architecture

A FastAPI web application wired up with a full monitoring pipeline for **metrics** (Prometheus) and **logs** (Loki), all visualized through **Grafana**.

## High-Level Architecture

```
┌─────────────┐         ┌────────────┐         ┌───────────┐
│  FastAPI App │──scrape──▶ Prometheus │──data───▶  Grafana  │
│ (port 8000)  │         │ (port 9090)│         │(port 3000)│
└──────┬──────┘         └────────────┘         └─────┬─────┘
       │ writes logs                                  │
       ▼                                              │
   ./logs/app.log                                     │
       │                                              │
       ▼                                              │
┌──────────────┐       ┌────────────┐                 │
│ Grafana Alloy │──push──▶   Loki   │──data───────────┘
│ (log shipper) │       │(port 3100)│
└──────────────┘       └────────────┘
```

## Data Flow

1. **Metrics path** — The FastAPI app auto-exposes a `/metrics` endpoint. Prometheus scrapes it every 5 seconds and stores time-series data. Grafana queries Prometheus to render dashboards.
2. **Logs path** — The FastAPI app writes structured logs to `./logs/app.log`. Grafana Alloy tails that file and pushes log lines to Loki. Grafana queries Loki to display and search logs.

---

## Component Details

### 1. FastAPI App — `main.py`

- Minimal FastAPI server with a single `GET /` endpoint.
- The endpoint **intentionally triggers a `ZeroDivisionError`** (`print(1/0)`) to demonstrate error logging — every request hits the `except` block and logs an error.
- Uses [`prometheus-fastapi-instrumentator`](https://github.com/trallnag/prometheus-fastapi-instrumentator) to auto-expose a `/metrics` endpoint with HTTP request metrics (latency, count, status codes, etc.).

```python
Instrumentator().instrument(app).expose(app)
```

### 2. Logging — `logging_config.py`

- Configures Python's built-in `logging` module to write log lines to `logs/app.log`.
- Log format: `%(asctime)s %(levelname)s %(message)s`
- Example output:
  ```
  2026-07-19 22:00:00,123 ERROR Error found division by zero
  ```

### 3. Prometheus — `prometheus.yml`

Prometheus is the **metrics store and query engine**. It is configured with two scrape targets:

| Job | Target | Purpose |
|-----|--------|---------|
| `prometheus` | `localhost:9090` | Internal Prometheus metrics |
| `fastapi` | `host.docker.internal:8000` | FastAPI `/metrics` endpoint |

- **Scrape interval**: every 5 seconds.
- `host.docker.internal` allows the Prometheus container to reach the FastAPI app running on the host machine.

### 4. Grafana Alloy — `config.alloy`

Grafana Alloy is a **log collector/shipper**. It is configured to:

1. **Discover** — `local.file_match` finds all `.log` files under `/logs/`.
2. **Tail** — `loki.source.file` reads new lines from matched files.
3. **Ship** — `loki.write` pushes log entries to Loki at `http://loki:3100/loki/api/v1/push`.

### 5. Docker Compose — `docker-compose.yml`

Spins up four containers that form the observability backend:

| Service | Image | Port | Role |
|---------|-------|------|------|
| **Prometheus** | `prom/prometheus:latest` | 9090 | Metrics store & query engine |
| **Grafana** | `grafana/grafana:latest` | 3000 | Visualization & dashboards |
| **Loki** | `grafana/loki:latest` | 3100 | Log aggregation & query engine |
| **Alloy** | `grafana/alloy:latest` | — | Log shipper (`./logs/` → Loki) |

Key volume mounts:
- `./prometheus.yml` → Prometheus config
- `./config.alloy` → Alloy config
- `./logs` → shared log directory so Alloy can read `app.log`
- `grafana-storage` → persistent Grafana data (dashboards, settings)

> **Note:** The FastAPI app runs **locally on the host** (not inside Docker), while the entire observability stack runs in Docker.

---

## How to Run

### 1. Start the observability stack

```bash
docker compose up -d
```

### 2. Start the FastAPI app

```bash
uvicorn main:app --reload
```

### 3. Generate traffic

```bash
curl http://localhost:8000/
```

Each request triggers the intentional error, producing both a metric data point and a log entry.

### 4. Explore in Grafana

Open [http://localhost:3000](http://localhost:3000) and add data sources:

- **Prometheus** → `http://prometheus:9090`
- **Loki** → `http://loki:3100`

---

## Dependencies

Defined in `pyproject.toml`:

| Package | Purpose |
|---------|---------|
| `fastapi` | Web framework |
| `uvicorn` | ASGI server |
| `prometheus-fastapi-instrumentator` | Auto-instruments FastAPI with Prometheus metrics |

Python version: `>= 3.13`
