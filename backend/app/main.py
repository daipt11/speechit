from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.routes import synthesize, voices

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
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Routers
app.include_router(voices.router, prefix="/api")
app.include_router(synthesize.router, prefix="/api")
