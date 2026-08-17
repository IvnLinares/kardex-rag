from app.main import app


def test_health_route_registered() -> None:
    assert "/api/health" in app.openapi()["paths"]
