from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_chat_route_registered() -> None:
    assert "/api/chat" in app.openapi()["paths"]


def test_chat_rejects_empty_question() -> None:
    response = client.post("/api/chat", json={"question": "   "})
    assert response.status_code == 422


def test_chat_rejects_too_long_question() -> None:
    response = client.post("/api/chat", json={"question": "a" * 501})
    assert response.status_code == 422
