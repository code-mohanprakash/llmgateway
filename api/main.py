"""
Main FastAPI application for Model Bridge SaaS
"""
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import time
import uuid
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response

# Import routers
from api.routers import auth, dashboard, llm, admin, billing, rbac, sso, ab_testing, contact, orchestration, documentation, api_playground, monitoring

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

app = FastAPI(
    title="Model Bridge SaaS",
description="Enhanced Multi-Provider Model Bridge with Intelligent Routing",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add request ID and timing"""
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    # Add request ID to headers
    request.state.request_id = request_id
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = request_id
    
    # Update metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    REQUEST_DURATION.observe(process_time)
    
    return response


# Include routers
app.include_router(documentation.router, prefix="/api/documentation", tags=["documentation"])
app.include_router(api_playground.router, prefix="/api/playground", tags=["playground"])
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(llm.router, prefix="/api/v1", tags=["llm"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(billing.router, prefix="/api/billing", tags=["billing"])
app.include_router(rbac.router, prefix="/api/rbac", tags=["rbac"])
app.include_router(sso.router, prefix="/api/sso", tags=["sso"])
app.include_router(ab_testing.router, prefix="/api/ab-testing", tags=["ab-testing"])
app.include_router(contact.router, prefix="/api/v1", tags=["contact"])
app.include_router(orchestration.router, prefix="/api", tags=["orchestration"])
app.include_router(monitoring.router, prefix="/api", tags=["monitoring"])

# Serve static files (frontend) - only if directory exists
import os
if os.path.exists("web/build/static"):
    app.mount("/static", StaticFiles(directory="web/build/static"), name="static")


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type="text/plain")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": time.time()}


@app.get("/api/health")
async def api_health_check():
    """API health check endpoint"""
    return {"status": "healthy", "version": "2.0.0"}


# Serve frontend for all other routes
@app.get("/{path:path}")
async def serve_frontend(path: str):
    """Serve React frontend"""
    # Serve index.html for client-side routing if it exists
    if os.path.exists("web/build/index.html"):
        return FileResponse("web/build/index.html")
    else:
        return {"message": "Frontend not built yet. Please run 'npm run build' in the web directory."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)