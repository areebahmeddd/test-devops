FastAPI app monitored by Uptime Kuma.

## Stack

| Service           | URL                        |
|-------------------|----------------------------|
| FastAPI           | <http://localhost:8000>    |
| Uptime Kuma       | <http://localhost:3001>    |
| Prometheus        | <http://localhost:9090>    |
| Grafana           | <http://localhost:3000>    |
| Blackbox Exporter | <http://localhost:9115>    |

## Setup

1. Copy `.env.example` to `.env` and fill in your Jira credentials.
2. In Uptime Kuma, add a **Webhook** notification pointing to your Jira bridge, then attach it to the FastAPI monitor.

```bash
docker compose up -d
```

## Testing the Jira integration

**Trigger a failure:**

```bash
curl -X POST http://localhost:8000/api/v1/toggle-error
```

Wait ~60-90 seconds for Uptime Kuma to detect the 503 and fire the webhook. A new ticket should appear in your Jira KAN board.

**Restore:**

```bash
curl -X POST http://localhost:8000/api/v1/toggle-error
```

Wait another ~60-90 seconds. The ticket should be auto-resolved.

**Check current error state:**

```bash
curl http://localhost:8000/api/v1/error-state
```

## Jira note

Use a **Webhook** notification type in Uptime Kuma, not `JiraServiceManagement`. The JSM type targets the Opsgenie alerting API which requires a paid JSM Operations plan.
