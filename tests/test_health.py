from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["versao"] == "1.0.0"
    assert "timestamp" in data
