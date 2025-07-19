"""
Input validation utilities for API endpoints
"""
import re
import html
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, validator
from fastapi import HTTPException, status

class APIValidationError(HTTPException):
    """Custom validation error"""
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

def sanitize_html_input(text: str) -> str:
    """Sanitize HTML input to prevent XSS"""
    if not text:
        return text
    return html.escape(text.strip())

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password_strength(password: str) -> List[str]:
    """Validate password strength and return list of errors"""
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one digit")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    return errors

def validate_organization_name(name: str) -> bool:
    """Validate organization name"""
    if not name or len(name.strip()) < 2:
        return False
    if len(name) > 100:
        return False
    # Allow alphanumeric, spaces, hyphens, underscores
    pattern = r'^[a-zA-Z0-9\s\-_]+$'
    return bool(re.match(pattern, name))

def validate_api_key_name(name: str) -> bool:
    """Validate API key name"""
    if not name or len(name.strip()) < 1:
        return False
    if len(name) > 50:
        return False
    # Allow alphanumeric, spaces, hyphens, underscores
    pattern = r'^[a-zA-Z0-9\s\-_]+$'
    return bool(re.match(pattern, name))

def validate_json_size(data: Dict[Any, Any], max_size_kb: int = 100) -> bool:
    """Validate JSON payload size"""
    import json
    import sys
    
    try:
        json_str = json.dumps(data)
        size_kb = sys.getsizeof(json_str) / 1024
        return size_kb <= max_size_kb
    except Exception:
        return False

def validate_workflow_name(name: str) -> bool:
    """Validate workflow name"""
    if not name or len(name.strip()) < 2:
        return False
    if len(name) > 100:
        return False
    # Allow alphanumeric, spaces, hyphens, underscores
    pattern = r'^[a-zA-Z0-9\s\-_]+$'
    return bool(re.match(pattern, name))

class ContactFormValidator(BaseModel):
    """Contact form validation"""
    name: str
    email: str
    company: Optional[str] = None
    message: str
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        if len(v) > 100:
            raise ValueError('Name must be less than 100 characters')
        return sanitize_html_input(v)
    
    @validator('email')
    def validate_email_field(cls, v):
        if not validate_email(v):
            raise ValueError('Invalid email format')
        return v.lower().strip()
    
    @validator('company')
    def validate_company(cls, v):
        if v and len(v) > 100:
            raise ValueError('Company name must be less than 100 characters')
        return sanitize_html_input(v) if v else v
    
    @validator('message')
    def validate_message(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('Message must be at least 10 characters long')
        if len(v) > 5000:
            raise ValueError('Message must be less than 5000 characters')
        return sanitize_html_input(v)

def validate_rate_limit_values(per_minute: int, per_hour: int, per_day: int) -> List[str]:
    """Validate rate limit values"""
    errors = []
    
    if per_minute < 0 or per_minute > 10000:
        errors.append("Per minute limit must be between 0 and 10000")
    
    if per_hour < 0 or per_hour > 100000:
        errors.append("Per hour limit must be between 0 and 100000")
    
    if per_day < 0 or per_day > 1000000:
        errors.append("Per day limit must be between 0 and 1000000")
    
    # Logical validation
    if per_minute * 60 > per_hour:
        errors.append("Per hour limit should be greater than per minute * 60")
    
    if per_hour * 24 > per_day:
        errors.append("Per day limit should be greater than per hour * 24")
    
    return errors

def sanitize_search_query(query: str) -> str:
    """Sanitize search query to prevent injection"""
    if not query:
        return ""
    
    # Remove special characters that could be used for injection
    sanitized = re.sub(r'[^\w\s\-]', '', query)
    return sanitized.strip()[:100]  # Limit length

def validate_pagination_params(page: int, limit: int) -> Dict[str, int]:
    """Validate and normalize pagination parameters"""
    # Ensure positive values
    page = max(1, page)
    limit = max(1, min(100, limit))  # Cap at 100 items per page
    
    return {"page": page, "limit": limit}