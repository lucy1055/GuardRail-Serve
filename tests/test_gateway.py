import uuid
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_pii_masking_and_uuid_routing() -> None:
    payload = {"prompt": "Hello Ram, please process this request."}
    response = client.post("/infer", json=payload)

    assert response.status_code == 200
    data = response.json()

    # Verify UUID format
    parsed_uuid = uuid.UUID(data["request_id"])
    assert str(parsed_uuid) == data["request_id"]

    # Verify PII masking
    assert "[REDACTED]" in data["masked_prompt"]
    assert "Ram" not in data["masked_prompt"]
    assert data["redacted_count"] >= 1