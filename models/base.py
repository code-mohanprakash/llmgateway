"""
Base models and mixins for the SaaS platform
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean
from database.database import Base


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class UUIDMixin:
    """Mixin for UUID primary key"""
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))


class SoftDeleteMixin:
    """Mixin for soft delete functionality"""
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)


class BaseModel(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """Base model with all common fields"""
    __abstract__ = True