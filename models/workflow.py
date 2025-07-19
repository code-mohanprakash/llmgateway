"""
Workflow models for orchestration system
"""
from sqlalchemy import Column, String, Text, Integer, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from models.base import BaseModel


class Workflow(BaseModel):
    """Workflow model for multi-step AI operations"""
    __tablename__ = "workflows"

    name = Column(String(200), nullable=False)
    description = Column(Text)
    definition = Column(JSON, nullable=False)  # Workflow definition as JSON
    version = Column(Integer, default=1)
    status = Column(String(20), default='draft')  # draft, active, inactive, archived
    
    # Foreign keys
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    organization = relationship("Organization")
    created_by_user = relationship("User")
    executions = relationship("WorkflowExecution", back_populates="workflow")


class WorkflowExecution(BaseModel):
    """Workflow execution tracking"""
    __tablename__ = "workflow_executions"

    workflow_id = Column(String(36), ForeignKey("workflows.id"), nullable=False)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    
    # Execution data
    input_data = Column(JSON)  # Input data for the workflow
    output_data = Column(JSON)  # Output data from the workflow
    status = Column(String(20), default='running')  # running, completed, failed, cancelled
    
    # Timing
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Results
    error_message = Column(Text)
    execution_time_ms = Column(Integer)
    total_cost = Column(Integer)  # Cost in cents
    
    # Relationships
    workflow = relationship("Workflow", back_populates="executions")
    organization = relationship("Organization")


class WorkflowStep(BaseModel):
    """Individual workflow step definition"""
    __tablename__ = "workflow_steps"

    workflow_id = Column(String(36), ForeignKey("workflows.id"), nullable=False)
    step_order = Column(Integer, nullable=False)
    step_type = Column(String(50), nullable=False)  # llm_call, data_processing, condition, etc.
    name = Column(String(200), nullable=False)
    description = Column(Text)
    configuration = Column(JSON, nullable=False)  # Step-specific configuration
    dependencies = Column(JSON)  # List of step IDs this step depends on
    
    # Relationships
    workflow = relationship("Workflow")


class WorkflowConnection(BaseModel):
    """Connections between workflow steps"""
    __tablename__ = "workflow_connections"

    workflow_id = Column(String(36), ForeignKey("workflows.id"), nullable=False)
    from_step_id = Column(String(36), ForeignKey("workflow_steps.id"), nullable=False)
    to_step_id = Column(String(36), ForeignKey("workflow_steps.id"), nullable=False)
    condition = Column(JSON)  # Conditional logic for the connection
    
    # Relationships
    workflow = relationship("Workflow") 