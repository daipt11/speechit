"""Smoke tests for the FastAPI skeleton."""

import os

import pytest
from fastapi.testclient import TestClient

# Provide a dummy API key so config.py doesn't raise at import time
os.environ.setdefault("GEMINI_API_KEY", "test-key-placeholder")

from app.main import app  # noqa: E402

client = TestClient(app)


def test_get_voices_returns_200():
    response = client.get("/api/voices")
    assert response.status_code == 200


def test_get_voices_returns_expected_list():
    response = client.get("/api/voices")
    data = response.json()
    assert "voices" in data
    assert data["voices"] == ["Kore", "Puck", "Aoede", "Charon", "Fenrir"]


from unittest.mock import patch

def test_post_synthesize_returns_200():
    fake_audio = b"RIFF\x00\x00\x00\x00WAVEfmt "
    with patch("app.routes.synthesize.synthesize", return_value=fake_audio):
        response = client.post("/api/synthesize", json={"text": "hello", "voice": "Kore"})
    assert response.status_code == 200
