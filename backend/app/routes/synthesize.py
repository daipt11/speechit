from fastapi import APIRouter, Request, Response

router = APIRouter()


@router.post("/synthesize")
async def synthesize_speech(request: Request) -> Response:
    """Stub endpoint — returns 501 Not Implemented. Implemented in TTS-05."""
    return Response(
        content='{"error": "not_implemented", "message": "Synthesis not yet implemented"}',
        status_code=501,
        media_type="application/json",
    )
