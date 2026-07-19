# Monitoring

A FastAPI application with a full observability stack — **Prometheus** for metrics, **Grafana** for dashboards, **Loki** for log aggregation, and **Grafana Alloy** for log collection.

## Architecture

```
┌─────────────┐        scrape /metrics         ┌────────────────┐
│   FastAPI    │ ◄──────────────────────────────│   Prometheus   │
│  :8000       │                                │   :9090        │
└──────┬───────┘                                └───────┬────────┘
       │ writes                                         │
       ▼                                                │  data source
  logs/app.log                                          │
       │                                                ▼
       │  tail                                   ┌──────────────┐
  ┌────┴──────┐      push       ┌──────────┐    │   Grafana     │
  │  Alloy    │ ───────────────►│   Loki   │───►│   :3000       │
  │           │                 │  :3100   │    │               │
  └───────────┘                 └──────────┘    └───────────────┘
```

| Service    | Port   | Purpose                                      |
| ---------- | ------ | -------------------------------------------- |
| FastAPI    | `8000` | Application server exposing `/metrics`        |
| Prometheus | `9090` | Scrapes FastAPI metrics every 5 s             |
| Grafana    | `3000` | Dashboards for metrics and logs               |
| Loki       | `3100` | Log storage backend                           |
| Alloy      | —      | Tails `logs/*.log` and ships them to Loki     |

## Prerequisites

- **Python** ≥ 3.13
- **uv** (Python package manager)
- **Docker** & **Docker Compose**

## Getting Started

### 1. Clone the repository

```bash
git clone <repo-url>
cd monitoring
```

### 2. Install Python dependencies

```bash
uv sync
```

### 3. Start the observability stack

```bash
docker compose up -d
```

This brings up Prometheus, Grafana, Loki, and Alloy.

### 4. Run the FastAPI app

```bash
uv run uvicorn main:app --reload
```

The app will be available at [http://localhost:8000](http://localhost:8000).

## Project Structure

```
monitoring/
├── main.py              # FastAPI app with Prometheus instrumentation
├── logging_config.py    # File-based logging setup (logs/app.log)
├── docker-compose.yml   # Prometheus, Grafana, Loki, Alloy services
├── prometheus.yml       # Prometheus scrape config
├── config.alloy         # Grafana Alloy pipeline — tails logs → Loki
├── pyproject.toml       # Project metadata & dependencies
├── logs/
│   └── app.log          # Application log output
└── README.md
```

## Configuration

### Prometheus (`prometheus.yml`)

- **Scrape interval**: 5 seconds
- **Targets**:
  - `localhost:9090` — Prometheus self-monitoring
  - `host.docker.internal:8000` — FastAPI `/metrics` endpoint

### Grafana Alloy (`config.alloy`)

Alloy tails all `*.log` files under `/logs` and pushes them to Loki at `http://loki:3100/loki/api/v1/push`.

### Logging (`logging_config.py`)

Logs are written to `logs/app.log` with the format:

```
%(asctime)s %(levelname)s %(message)s
```

## Dependencies

| Package                              | Version   |
| ------------------------------------ | --------- |
| `fastapi`                            | ≥ 0.139.2 |
| `uvicorn`                            | ≥ 0.51.0  |
| `prometheus-fastapi-instrumentator`  | ≥ 8.0.2   |

## Usage

Once everything is running:

- **FastAPI** — [http://localhost:8000](http://localhost:8000)
- **Prometheus UI** — [http://localhost:9090](http://localhost:9090)
- **Grafana** — [http://localhost:3000](http://localhost:3000) (default credentials: `admin` / `admin`)

In Grafana, add **Prometheus** (`http://prometheus:9090`) and **Loki** (`http://loki:3100`) as data sources to start building dashboards.

## License

MIT
