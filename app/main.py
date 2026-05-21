from fastapi import FastAPI, HTTPException
import time
import random

app = FastAPI(
    title="Test API",
    description="Boilerplate API for testing incident management integrations",
    version="1.0.0",
)

# Simple in-memory toggle to simulate downtime
_force_error = False


@app.get("/")
def root():
    return {
        "service": "test-api",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
def health():
    """Primary health check endpoint."""
    if _force_error:
        raise HTTPException(status_code=503, detail="Service deliberately degraded for incident testing")
    return {"status": "healthy", "timestamp": time.time()}


@app.get("/api/v1/items")
def get_items():
    """Sample data endpoint."""
    if _force_error:
        raise HTTPException(status_code=500, detail="Internal server error (simulated)")
    return {
        "items": [
            {"id": 1, "name": "Widget A", "stock": 42},
            {"id": 2, "name": "Widget B", "stock": 7},
            {"id": 3, "name": "Widget C", "stock": 0},
        ]
    }


@app.get("/api/v1/slow")
def slow_endpoint():
    """Slow endpoint for testing timeout alerting."""
    time.sleep(random.uniform(2, 5))
    return {"status": "ok", "note": "This endpoint is intentionally slow"}


@app.post("/api/v1/toggle-error")
def toggle_error():
    """Toggle simulated error mode ON/OFF to manually trigger and resolve an incident."""
    global _force_error
    _force_error = not _force_error
    state = "ON (degraded)" if _force_error else "OFF (healthy)"
    return {
        "error_mode": _force_error,
        "message": f"Error simulation is now {state}",
    }


@app.get("/api/v1/error-state")
def error_state():
    return {"error_mode": _force_error}
