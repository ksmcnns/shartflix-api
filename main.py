import logging
import sys
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from routes.auth import router as auth_router
from routes.movies import router as movies_router

# Loglama yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger("movie_api")

app = FastAPI(
    title="Movie API",
    description="API for user authentication and movie management",
    version="1.0.0",
)

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
    "http://192.168.1.116:8000",  # Flutter local IP
    "http://10.0.2.2:8000",  # Android emulator için (opsiyonel)
    "*"  # Development için, production'da kaldır
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api", tags=["auth"])
app.include_router(movies_router, prefix="/api", tags=["movies"])  # /api + /movie/list = /api/movie/list

# Middleware (uvicorn log ile çakışmasın diye log_config kaldırıldı)
@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Movie API server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        # log_config=None  # Kaldır, middleware yeterli
    )