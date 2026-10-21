from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .api.routes import router as api_router
from .db.database import init_db

limiter = Limiter(key_func=get_remote_address, default_limits=["10/minute"])

app = FastAPI(title='VulTure Security Scanner', version='1.0.0')
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.on_event("startup")
def startup_event():
    init_db()

# Root endpoint to prevent 404 on base URL
@app.get("/")
def read_root():
    return {"status": "online", "docs": "/docs"}

# CORS – allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Mount router without duplicate prefix
app.include_router(api_router)