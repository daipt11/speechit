import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

# Provide a dummy API key so config.py doesn't raise at import time
os.environ.setdefault("GEMINI_API_KEY", "test-key")

from app.main import app
from app.tts_client import VOICES

client = TestClient(app)

def test_get_voices_returns_five():
    resp = client.get("/api/voices")
    assert resp.status_code == 200
    data = resp.json()
    assert set(data["voices"]) == {"Kore", "Puck", "Aoede", "Charon", "Fenrir"}
    assert len(data["voices"]) == 5

def test_synthesize_returns_wav():
    fake_audio = b"RIFF\x00\x00\x00\x00WAVEfmt "
    with patch("app.routes.synthesize.synthesize", return_value=fake_audio):
        resp = client.post("/api/synthesize", json={"text": "hello", "voice": "Kore"})
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "audio/wav"
    assert resp.headers["content-disposition"] == 'attachment; filename="speechit.wav"'
    assert resp.content == fake_audio

def test_synthesize_rejects_empty_text():
    resp = client.post("/api/synthesize", json={"text": "", "voice": "Kore"})
    assert resp.status_code == 422
    data = resp.json()
    assert data["error"] == "text_required"
    assert "empty" in data["message"].lower() or "required" in data["message"].lower()

def test_synthesize_rejects_long_text():
    resp = client.post("/api/synthesize", json={"text": "a" * 6001, "voice": "Kore"})
    assert resp.status_code == 422
    data = resp.json()
    assert data["error"] == "input_too_long"
    assert "6000" in data["message"]

def test_synthesize_rejects_invalid_voice():
    resp = client.post("/api/synthesize", json={"text": "hello", "voice": "Unknown"})
    assert resp.status_code == 422
    data = resp.json()
    assert data["error"] == "invalid_voice"
    assert "Unknown" in data["message"]

def test_synthesize_rejects_long_style_prompt():
    resp = client.post("/api/synthesize", json={"text": "hello", "voice": "Kore", "style_prompt": "a" * 501})
    assert resp.status_code == 422
    data = resp.json()
    assert data["error"] == "validation_error"
    assert "style_prompt" in data["message"]

def test_synthesize_rate_limiting():
    # Clear the rate limit storage state so we start with a clean budget
    from app.routes.synthesize import limiter as synth_limiter
    synth_limiter.limiter.storage.reset()

    fake_audio = b"RIFF\x00\x00\x00\x00WAVEfmt "
    with patch("app.routes.synthesize.synthesize", return_value=fake_audio):
        for _ in range(10):
            resp = client.post("/api/synthesize", json={"text": "hello", "voice": "Kore"})
            assert resp.status_code == 200
        
        # 11th request should trigger rate limit (429)
        resp = client.post("/api/synthesize", json={"text": "hello", "voice": "Kore"})
        assert resp.status_code == 429
        data = resp.json()
        assert data["error"] == "rate_limit_exceeded"
        assert "Retry-After" in resp.headers
