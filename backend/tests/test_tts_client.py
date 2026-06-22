import pytest
from unittest.mock import patch, MagicMock

def _mock_client(audio_bytes=b"RIFF\x00\x00\x00\x00WAVEfmt "):
    mock_client = MagicMock()
    mock_part = MagicMock()
    mock_part.inline_data.data = audio_bytes
    mock_client.models.generate_content.return_value.candidates[0].content.parts = [mock_part]
    return mock_client

def test_synthesize_uses_correct_model(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    mock_client = _mock_client()
    with patch("app.tts_client.genai.Client", return_value=mock_client):
        from app.tts_client import synthesize
        synthesize("Hello world", "Kore")
    assert mock_client.models.generate_content.call_args.kwargs["model"] == "gemini-3.1-flash-tts-preview"

def test_synthesize_with_style_prompt(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    mock_client = _mock_client()
    with patch("app.tts_client.genai.Client", return_value=mock_client):
        from app.tts_client import synthesize
        synthesize("Hello", "Puck", style_prompt="speak slowly")
    contents = mock_client.models.generate_content.call_args.kwargs["contents"]
    assert "speak slowly" in contents
    assert "Hello" in contents

def test_synthesize_raises_without_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    import importlib, app.tts_client as m
    importlib.reload(m)
    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        m.synthesize("Hello", "Kore")
