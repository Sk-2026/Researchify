
from fastapi import FastAPI

app = FastAPI(
    title="Researchify API",
    description="Your personalized AI research companion",
    version="0.1.0",
)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Researchify!",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "researchify-backend",
    }
