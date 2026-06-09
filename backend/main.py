from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router


app = FastAPI(
    title="Tello AI Web Interface API",
    description=(
        "Local API for translating natural-language commands into "
        "validated DJI Tello actions and Python code."
    ),
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    router,
    prefix="/api",
    tags=["Tello pipeline"],
)


@app.get("/")
def root():
    return {
        "message": "Tello AI Web Interface API is running.",
        "documentation": "/docs",
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "execution_mode": "local",
    }