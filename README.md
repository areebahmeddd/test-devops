FastAPI service monitored by a self-hosted OneUptime stack.

## Stack

| Service      | Image                               | Role                                          |
| ------------ | ----------------------------------- | --------------------------------------------- |
| `fastapi`    | local build                         | FastAPI application - `http://localhost:8000` |
| `app`        | `oneuptime/app:release`             | OneUptime platform (API, workers, dashboard)  |
| `probe`      | `oneuptime/probe:release`           | Monitoring probe running on host network      |
| `ingress`    | `oneuptime/nginx:release`           | NGINX reverse proxy - `http://localhost`      |
| `postgres`   | `postgres:18-alpine`                | Primary PostgreSQL database                   |
| `clickhouse` | `clickhouse/clickhouse-server:26.4` | Telemetry and time-series database            |
| `redis`      | `redis:8.2-alpine`                  | Cache and background job queue                |

## Setup

1. Copy the environment file:

   ```bash
   cp .env.example .env
   ```

2. Start the stack:

   ```bash
   docker compose up -d
   ```

3. Wait approximately 2 minutes for database initialization and migrations.

## Access

| URL                                         | Description             |
| ------------------------------------------- | ----------------------- |
| `http://localhost`                          | OneUptime dashboard     |
| `http://localhost:8000/health`              | FastAPI health endpoint |
| `http://localhost:8000/api/v1/toggle-error` | Toggle error mode       |
| `http://localhost:8000/api/v1/error-state`  | Current error state     |

## OneUptime Configuration

1. Open `http://localhost`
2. Create an account
3. Create a project
4. Create an API monitor targeting:

```text
http://localhost:8000/health
```

The probe automatically registers and starts monitoring the FastAPI service.

## FastAPI Endpoints

| Method | Endpoint               | Description                              |
| ------ | ---------------------- | ---------------------------------------- |
| `GET`  | `/health`              | Returns `200 healthy` or `503 unhealthy` |
| `POST` | `/api/v1/toggle-error` | Toggle error mode                        |
| `GET`  | `/api/v1/error-state`  | Get current error mode                   |
