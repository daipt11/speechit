from fastapi import APIRouter
from app.tts_client import VOICES

router = APIRouter()


@router.get("/voices")
async def list_voices() -> dict:
    """List available TTS voices. Returns a static list from tts_client."""
    return {"voices": VOICES}
