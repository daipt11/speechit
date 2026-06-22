from fastapi import APIRouter, Request, Response
from pydantic import BaseModel, field_validator
from app.tts_client import synthesize, VOICES
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

MAX_CHARS = 6000


class SynthesizeRequest(BaseModel):
    text: str
    voice: str
    style_prompt: str | None = None

    @field_validator("text")
    @classmethod
    def text_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("text_required")
        if len(v) > MAX_CHARS:
            raise ValueError("input_too_long")
        return v

    @field_validator("voice")
    @classmethod
    def voice_must_be_valid(cls, v):
        if v not in VOICES:
            raise ValueError("invalid_voice")
        return v

    @field_validator("style_prompt")
    @classmethod
    def style_prompt_length(cls, v):
        if v and len(v) > 500:
            raise ValueError("style_prompt too long (max 500 chars)")
        return v


@router.post("/synthesize")
@limiter.limit("10/minute")
async def synthesize_speech(request: Request, body: SynthesizeRequest) -> Response:
    audio_bytes = synthesize(body.text, body.voice, body.style_prompt)
    return Response(
        content=audio_bytes,
        media_type="audio/wav",
        headers={"Content-Disposition": 'attachment; filename="speechit.wav"'},
    )
