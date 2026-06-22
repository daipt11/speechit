import os
from google import genai
from google.genai import types

VOICES = ["Kore", "Puck", "Aoede", "Charon", "Fenrir"]
MODEL = "gemini-3.1-flash-tts-preview"

def _get_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable is not set")
    return genai.Client(api_key=api_key)

def synthesize(text: str, voice: str, style_prompt: str | None = None) -> bytes:
    """Call Gemini TTS and return raw WAV bytes. No files written to disk."""
    client = _get_client()
    speech_config = types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice)
        )
    )
    contents = f"{style_prompt}\n\n{text}" if style_prompt else text
    response = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=speech_config,
        ),
    )
    return response.candidates[0].content.parts[0].inline_data.data
