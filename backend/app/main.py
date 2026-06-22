from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.routes import synthesize, voices
from app.tts_client import VOICES

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="SpeechIt API",
    description="TTS demo powered by Google Gemini API",
    version="1.0.0",
)

# CORS — allow all origins for demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": "Rate limit exceeded. Please wait 60 seconds before retrying."
        },
        headers={"Retry-After": "60"}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    if not errors:
        return JSONResponse(
            status_code=422,
            content={"error": "validation_error", "message": str(exc)}
        )
    
    first_err = errors[0]
    loc = first_err.get("loc", [])
    msg = first_err.get("msg", "")
    err_type = first_err.get("type", "")
    invalid_value = first_err.get("input", "")
    
    error_code = "validation_error"
    error_message = msg
    
    if err_type == "missing":
        if "text" in loc:
            error_code = "text_required"
            error_message = "text field is required and must not be empty"
        elif "voice" in loc:
            error_code = "invalid_voice"
            error_message = f"Voice is not supported. Allowed values: {', '.join(VOICES)}"
    else:
        if "text_required" in msg:
            error_code = "text_required"
            error_message = "text field is required and must not be empty"
        elif "input_too_long" in msg:
            error_code = "input_too_long"
            error_message = "Text exceeds the maximum allowed length of 6000 characters"
        elif "invalid_voice" in msg:
            error_code = "invalid_voice"
            error_message = f"Voice '{invalid_value}' is not supported. Allowed values: {', '.join(VOICES)}"
        elif "style_prompt" in msg:
            error_code = "validation_error"
            # Extract prompt limit detail
            error_message = "style_prompt too long (max 500 chars)"

    return JSONResponse(
        status_code=422,
        content={"error": error_code, "message": error_message}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error", "message": "An unexpected error occurred"},
    )

# Routers
app.include_router(voices.router, prefix="/api")
app.include_router(synthesize.router, prefix="/api")
