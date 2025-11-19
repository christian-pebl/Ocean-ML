"""
Ocean-ML Backend API

FastAPI application for managing video annotations, training runs,
and model inference.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
from routers import videos, annotations

# Create FastAPI app
app = FastAPI(
    title="Ocean-ML API",
    description="Collaborative Fish Detection & Annotation Platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "service": "ocean-ml-api"
    }

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Ocean-ML API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }

# Supabase connection test endpoint
@app.get("/supabase-test", tags=["health"])
async def test_supabase_connection():
    """Test Supabase connection"""
    try:
        from services.supabase_client import get_supabase_client

        supabase = get_supabase_client()

        # Try to list buckets
        buckets = supabase.storage.list_buckets()

        return {
            "status": "connected",
            "buckets": [b["name"] for b in buckets] if buckets else []
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

# Register routers
app.include_router(videos.router)
app.include_router(annotations.router)
# app.include_router(training.router)  # TODO: Create training router
# app.include_router(inference.router)  # TODO: Create inference router
# app.include_router(desktop.router)  # TODO: Create desktop router

# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("🚀 Ocean-ML API starting...")
    print(f"📍 Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"🔧 Debug mode: {os.getenv('DEBUG', 'True')}")
    print(f"🌐 CORS origins: {origins}")
    print("✅ API ready!")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print("👋 Ocean-ML API shutting down...")

# Run with: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True
    )
