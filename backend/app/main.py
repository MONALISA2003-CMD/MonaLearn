"""
MonaLearn API
=============
A minimal FastAPI backend that serves the data the frontend prototypes
(landing page, dashboard, AI tutor) currently mock in JavaScript. This is a
starting scaffold matching the "Technology Requirements" section of the
product spec (Python + FastAPI, PostgreSQL-ready), not a finished production
backend — see the root README for what's real vs. illustrative.

Run locally:
    cd backend
    pip install -r requirements.txt
    cp .env.example .env   # then add your ANTHROPIC_API_KEY
    uvicorn app.main:app --reload

Docs will be at http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_db
from app.routers import admin, auth, billing, certificates, courses, dashboard, instructor, maintenance, tutor

app = FastAPI(
    title="MonaLearn API",
    description="Backend for the MonaLearn learning platform prototype.",
    version="0.1.0",
)

# Wide open for local prototyping. Tighten allow_origins before any real deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # Prototype-grade: creates tables that don't exist yet. Switch to Alembic
    # migrations before this runs against a database with real data in it.
    init_db()


app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(instructor.router, prefix="/api/instructor", tags=["instructor"])
app.include_router(billing.router, prefix="/api/billing", tags=["billing"])
app.include_router(maintenance.router, prefix="/api/maintenance", tags=["maintenance"])
app.include_router(courses.router, prefix="/api/courses", tags=["courses"])
app.include_router(certificates.router, prefix="/api/certificates", tags=["certificates"])
app.include_router(tutor.router, prefix="/api/tutor", tags=["tutor"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])


@app.get("/api/health", tags=["health"])
def health_check():
    return {"status": "ok", "service": "monalearn-api"}
