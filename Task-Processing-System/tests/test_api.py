from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app


def sample_job() -> dict:
    return {
        "id": 1,
        "type": "fibonacci",
        "input": 10,
        "status": "COMPLETED",
        "result": 55,
        "error": None,
        "created_at": datetime.now(timezone.utc),
        "started_at": None,
        "completed_at": None,
    }


def test_root() -> None:
    assert TestClient(app).get("/").json()["status"] == "ok"


def test_invalid_request() -> None:
    response = TestClient(app).post("/jobs", json={"type": "nope", "input": 2})
    assert response.status_code == 422
    response = TestClient(app).post(
        "/jobs", json={"type": "prime_factorization", "input": 1}
    )
    assert response.status_code == 422


def test_job_routes(monkeypatch) -> None:
    from app import database

    monkeypatch.setattr(database, "create_job", lambda *_: 1)
    monkeypatch.setattr(database, "list_jobs", lambda: [sample_job()])
    monkeypatch.setattr(database, "get_job", lambda job_id: sample_job() if job_id == 1 else None)
    monkeypatch.setattr(database, "delete_job", lambda job_id: job_id == 1)
    client = TestClient(app)
    assert client.post("/jobs", json={"type": "fibonacci", "input": 10}).status_code == 201
    assert client.get("/jobs").status_code == 200
    assert client.get("/jobs/1").json()["result"] == 55
    assert client.get("/jobs/1/result").json()["result"] == 55
    assert client.get("/jobs/999").status_code == 404
    assert client.delete("/jobs/1").status_code == 204
    assert client.delete("/jobs/999").status_code == 404