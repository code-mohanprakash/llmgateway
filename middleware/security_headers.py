"""
Security headers middleware for FastAPI application
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse
import time

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        
        # Security headers
        security_headers = {
            # Prevent XSS attacks
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            
            # HSTS (HTTP Strict Transport Security)
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            
            # Content Security Policy
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://js.stripe.com; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https://api.stripe.com; "
                "frame-src https://js.stripe.com; "
                "object-src 'none'; "
                "base-uri 'self'"
            ),
            
            # Referrer Policy
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # Permissions Policy (formerly Feature Policy)
            "Permissions-Policy": (
                "camera=(), microphone=(), geolocation=(), "
                "usb=(), accelerometer=(), gyroscope=(), magnetometer=()"
            ),
            
            # Remove server information
            "Server": "ModelBridge",
            
            # Cache control for API responses
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
        
        # Apply security headers
        for header, value in security_headers.items():
            response.headers[header] = value
        
        # Remove potentially sensitive headers
        if "Server" in response.headers:
            response.headers["Server"] = "ModelBridge"
        
        return response

class RateLimitSecurityMiddleware(BaseHTTPMiddleware):
    """Rate limiting and request validation middleware"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = {}
        self.last_cleanup = time.time()
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Clean up old entries every minute
        current_time = time.time()
        if current_time - self.last_cleanup > 60:
            self._cleanup_old_entries(current_time)
            self.last_cleanup = current_time
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check rate limit
        if self._is_rate_limited(client_ip, current_time):
            return StarletteResponse(
                content="Rate limit exceeded",
                status_code=429,
                headers={"Retry-After": "60"}
            )
        
        # Validate request size
        if not await self._validate_request_size(request):
            return StarletteResponse(
                content="Request too large",
                status_code=413
            )
        
        # Proceed with request
        response = await call_next(request)
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request"""
        # Check for forwarded headers (reverse proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        return request.client.host if request.client else "unknown"
    
    def _is_rate_limited(self, client_ip: str, current_time: float) -> bool:
        """Check if client is rate limited"""
        minute_key = int(current_time // 60)
        
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = {}
        
        client_requests = self.request_counts[client_ip]
        current_count = client_requests.get(minute_key, 0)
        
        if current_count >= self.requests_per_minute:
            return True
        
        # Increment counter
        client_requests[minute_key] = current_count + 1
        return False
    
    def _cleanup_old_entries(self, current_time: float):
        """Remove old rate limit entries"""
        current_minute = int(current_time // 60)
        cutoff_minute = current_minute - 2  # Keep last 2 minutes
        
        for client_ip in list(self.request_counts.keys()):
            client_data = self.request_counts[client_ip]
            
            # Remove old minute entries
            for minute in list(client_data.keys()):
                if minute < cutoff_minute:
                    del client_data[minute]
            
            # Remove client if no recent requests
            if not client_data:
                del self.request_counts[client_ip]
    
    async def _validate_request_size(self, request: Request) -> bool:
        """Validate request content length"""
        max_size = 10 * 1024 * 1024  # 10MB
        
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                return size <= max_size
            except ValueError:
                return False
        
        return True