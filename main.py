#!/usr/bin/env python3
"""
Production FastAPI application for LLM Gateway SaaS
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
from api.routers import auth, dashboard, llm, admin, billing

app = FastAPI(
    title=os.getenv("APP_NAME", "LLM Gateway SaaS"),
    description="Production-ready Multi-Provider LLM Gateway",
    version=os.getenv("APP_VERSION", "2.0.0"),
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(llm.router, prefix="/api/v1", tags=["llm"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(billing.router, prefix="/api/billing", tags=["billing"])

# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": os.getenv("APP_VERSION", "2.0.0")}

@app.get("/api/health")
async def api_health_check():
    """API health check endpoint"""
    return {"status": "healthy", "version": os.getenv("APP_VERSION", "2.0.0")}

# Serve static files (production React build)
if os.path.exists("web/build/static"):
    app.mount("/static", StaticFiles(directory="web/build/static"), name="static")

# Serve React app for all other routes (SPA fallback)
@app.get("/{path:path}")
async def serve_react_app(path: str):
    """Serve React frontend for client-side routing"""
    if path.startswith("api/"):
        return {"error": "API endpoint not found"}, 404
    
    # Serve index.html for all other routes (client-side routing)
    if os.path.exists("web/build/index.html"):
        return FileResponse("web/build/index.html")
    else:
        return {"message": "Frontend not built. Please run 'cd web && npm run build'"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0", 
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )