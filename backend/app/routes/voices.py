from fastapi import APIRouter

router = APIRouter()

VOICES = ["Kore", "Puck", "Aoede", "Charon", "Fenrir"]


@router.get("/voices")
async def list_voices() -> dict:
    """List available TTS voices. Returns a static hardcoded list."""
    return {"voices": VOICES}
