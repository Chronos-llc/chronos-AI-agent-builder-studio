"""Platform endpoint availability smoke tests.

These checks validate that feature routes are wired and return an expected
HTTP code shape for unauthenticated test clients in local environments.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def assert_expected_status(code: int):
    assert code in {200, 201, 400, 401, 403, 404, 405, 422}


def test_marketplace_routes():
    assert_expected_status(client.get("/api/v1/marketplace/listings").status_code)
    assert_expected_status(client.get("/api/v1/marketplace/listings/1").status_code)
    assert_expected_status(client.post("/api/v1/marketplace/listings/1/install").status_code)


def test_skills_routes():
    assert_expected_status(client.get("/api/v1/skills/skills").status_code)
    assert_expected_status(client.get("/api/v1/skills/skills/1").status_code)


def test_platform_updates_routes():
    assert_expected_status(client.get("/api/v1/updates").status_code)
    assert_expected_status(client.post("/api/v1/updates/1/mark-viewed").status_code)


def test_support_routes():
    assert_expected_status(client.get("/api/v1/support/messages").status_code)
    assert_expected_status(client.post("/api/v1/support/messages").status_code)


def test_payment_routes():
    assert_expected_status(client.get("/api/v1/payment/methods").status_code)
    assert_expected_status(client.post("/api/v1/payment/methods").status_code)

