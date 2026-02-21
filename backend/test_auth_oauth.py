from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings

client = TestClient(app)


def test_oauth_start_rejects_unknown_provider():
    response = client.get('/api/v1/auth/oauth/unknown/start')
    assert response.status_code == 400


def test_oauth_start_requires_provider_configuration(monkeypatch):
    monkeypatch.setattr(settings, 'GOOGLE_OAUTH_CLIENT_ID', None)
    monkeypatch.setattr(settings, 'GOOGLE_OAUTH_CLIENT_SECRET', None)
    monkeypatch.setattr(settings, 'GOOGLE_OAUTH_REDIRECT_URI', None)

    response = client.get('/api/v1/auth/oauth/google/start')
    assert response.status_code == 400
    assert 'configured' in response.json().get('detail', '').lower()


def test_oauth_start_redirects_when_configured(monkeypatch):
    monkeypatch.setattr(settings, 'GOOGLE_OAUTH_CLIENT_ID', 'dummy-google-client-id')
    monkeypatch.setattr(settings, 'GOOGLE_OAUTH_CLIENT_SECRET', 'dummy-google-client-secret')
    monkeypatch.setattr(settings, 'GOOGLE_OAUTH_REDIRECT_URI', 'http://localhost:8000/api/v1/auth/oauth/google/callback')

    response = client.get('/api/v1/auth/oauth/google/start', follow_redirects=False)
    assert response.status_code in {302, 307}
    assert 'accounts.google.com' in response.headers.get('location', '')


def test_oauth_callback_rejects_invalid_state():
    response = client.get('/api/v1/auth/oauth/google/callback?code=abc&state=invalid_state')
    assert response.status_code == 401
