import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

os.environ.setdefault("GEMINI_API_KEY", "test-key")

from app.main import app
from app.routes.synthesize import limiter as synth_limiter

client = TestClient(app, raise_server_exceptions=False)


def _reset_rate_limit():
    """Reset slowapi storage so each test starts with a clean budget."""
    synth_limiter.limiter.storage.reset()


def test_upstream_error_returns_502():
    _reset_rate_limit()
    with patch("app.routes.synthesize.synthesize", side_effect=Exception("API error")):
        resp = client.post("/api/synthesize", json={"text": "hi", "voice": "Kore"})
    assert resp.status_code == 502
    body = resp.json()
    assert body["error"] == "upstream_error"
    assert "message" in body


def test_upstream_error_does_not_expose_api_key():
    _reset_rate_limit()
    with patch("app.routes.synthesize.synthesize", side_effect=Exception("API error")):
        resp = client.post("/api/synthesize", json={"text": "hi", "voice": "Kore"})
    body = resp.text
    assert "GEMINI_API_KEY" not in body
    assert "test-key" not in body


def test_rate_limit_returns_429_on_11th_request():
    _reset_rate_limit()
    fake_audio = b"RIFF\x00\x00\x00\x00WAVEfmt "
    with patch("app.routes.synthesize.synthesize", return_value=fake_audio):
        for i in range(10):
            r = client.post("/api/synthesize", json={"text": "hi", "voice": "Kore"})
            assert r.status_code == 200, f"Request {i+1} failed unexpectedly: {r.status_code}"
        resp = client.post("/api/synthesize", json={"text": "hi", "voice": "Kore"})
    assert resp.status_code == 429
    body = resp.json()
    assert body["error"] == "rate_limit_exceeded"
    assert "message" in body


def test_validation_422_has_error_and_message_empty_text():
    resp = client.post("/api/synthesize", json={"text": "", "voice": "Kore"})
    assert resp.status_code == 422
    body = resp.json()
    assert "error" in body
    assert "message" in body


def test_validation_422_has_error_and_message_invalid_voice():
    resp = client.post("/api/synthesize", json={"text": "hello", "voice": "Invalid"})
    assert resp.status_code == 422
    body = resp.json()
    assert "error" in body
    assert "message" in body


def test_validation_422_has_error_and_message_text_too_long():
    resp = client.post("/api/synthesize", json={"text": "a" * 6001, "voice": "Kore"})
    assert resp.status_code == 422
    body = resp.json()
    assert "error" in body
    assert "message" in body
