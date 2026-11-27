
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.recommendations import router as recommendations_router
from app.api.routes.feedback import router as feedback_router
from app.api.routes.auth import router as auth_router
from app.api.routes.profile import router as profile_router
from app.api.routes.discovery import router as discovery_router
from app.api.routes.paper_import import router as paper_import_router
from app.api.routes.notifications import router as notifications_router
from app.api.routes import papers


app = FastAPI(
    title="ZealWithin API",
    description="Your personalized AI research companion",
    version="0.1.0",
)


# Allow the Next.js frontend to communicate with FastAPI.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Welcome to ZealWithin!",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "zealwithin-backend",
    }


app.include_router(auth_router, prefix="/api/v1")
app.include_router(recommendations_router, prefix="/api/v1")
app.include_router(feedback_router, prefix="/api/v1")
app.include_router(profile_router, prefix="/api/v1")
app.include_router(discovery_router, prefix="/api/v1")
app.include_router(papers.router, prefix="/api/v1")
app.include_router(paper_import_router, prefix="/api/v1")
app.include_router(notifications_router, prefix="/api/v1")
