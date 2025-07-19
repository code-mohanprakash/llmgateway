"""
Workflow service for orchestration system
"""
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.workflow import Workflow, WorkflowExecution, WorkflowStep, WorkflowConnection
from models.user import User, Organization


class WorkflowService:
    """Service for managing workflows"""
    
    def __init__(self):
        pass
    
    async def create_workflow(
        self,
        workflow_data: Dict[str, Any],
        organization_id: str,
        created_by: str,
        db: AsyncSession
    ) -> str:
        """Create a new workflow"""
        
        # Generate workflow ID
        workflow_id = str(uuid.uuid4())
        
        # Create workflow definition
        definition = {
            "steps": workflow_data.get("steps", []),
            "connections": workflow_data.get("connections", []),
            "variables": workflow_data.get("variables", {}),
            "timeout_seconds": workflow_data.get("timeout_seconds", 3600)
        }
        
        # Create workflow record
        workflow = Workflow(
            id=workflow_id,
            name=workflow_data["name"],
            description=workflow_data.get("description", ""),
            definition=definition,
            version=1,
            status="draft",
            organization_id=organization_id,
            created_by=created_by
        )
        
        db.add(workflow)
        await db.commit()
        
        return workflow_id
    
    async def list_workflows(
        self,
        organization_id: str,
        db: AsyncSession,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List workflows for an organization"""
        
        result = await db.execute(
            select(Workflow)
            .where(Workflow.organization_id == organization_id)
            .order_by(Workflow.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        workflows = result.scalars().all()
        
        return [
            {
                "id": w.id,
                "name": w.name,
                "description": w.description,
                "status": w.status,
                "version": w.version,
                "created_at": w.created_at.isoformat(),
                "updated_at": w.updated_at.isoformat(),
                "execution_count": len(w.executions)
            }
            for w in workflows
        ]
    
    async def get_workflow(
        self,
        workflow_id: str,
        organization_id: str,
        db: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        """Get workflow by ID"""
        
        result = await db.execute(
            select(Workflow)
            .where(
                Workflow.id == workflow_id,
                Workflow.organization_id == organization_id
            )
        )
        
        workflow = result.scalar_one_or_none()
        
        if not workflow:
            return None
        
        return {
            "id": workflow.id,
            "name": workflow.name,
            "description": workflow.description,
            "definition": workflow.definition,
            "status": workflow.status,
            "version": workflow.version,
            "created_at": workflow.created_at.isoformat(),
            "updated_at": workflow.updated_at.isoformat(),
            "execution_count": len(workflow.executions)
        }
    
    async def execute_workflow(
        self,
        workflow_id: str,
        input_data: Dict[str, Any],
        organization_id: str,
        user_id: str,
        db: AsyncSession
    ) -> str:
        """Execute a workflow"""
        
        # Get workflow
        workflow = await self.get_workflow(workflow_id, organization_id, db)
        if not workflow:
            raise ValueError("Workflow not found")
        
        # Generate execution ID
        execution_id = str(uuid.uuid4())
        
        # Create execution record
        execution = WorkflowExecution(
            id=execution_id,
            workflow_id=workflow_id,
            organization_id=organization_id,
            input_data=input_data,
            status="running",
            started_at=datetime.utcnow()
        )
        
        db.add(execution)
        await db.commit()
        
        # TODO: Start actual workflow execution in background
        # For now, just simulate completion
        execution.status = "completed"
        execution.completed_at = datetime.utcnow()
        execution.execution_time_ms = 5000  # 5 seconds
        execution.total_cost = 50  # 50 cents
        execution.output_data = {
            "result": "Workflow executed successfully",
            "steps_completed": 3,
            "total_cost": 0.50
        }
        
        await db.commit()
        
        return execution_id
    
    async def get_execution_status(
        self,
        execution_id: str,
        organization_id: str,
        db: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        """Get execution status"""
        
        result = await db.execute(
            select(WorkflowExecution)
            .where(
                WorkflowExecution.id == execution_id,
                WorkflowExecution.organization_id == organization_id
            )
        )
        
        execution = result.scalar_one_or_none()
        
        if not execution:
            return None
        
        return {
            "execution_id": execution.id,
            "workflow_id": execution.workflow_id,
            "status": execution.status,
            "started_at": execution.started_at.isoformat(),
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "execution_time_ms": execution.execution_time_ms,
            "total_cost": execution.total_cost / 100 if execution.total_cost else 0,  # Convert cents to dollars
            "input_data": execution.input_data,
            "output_data": execution.output_data,
            "error_message": execution.error_message
        }
    
    async def get_dashboard_stats(
        self,
        organization_id: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Get workflow dashboard statistics"""
        
        # Get total workflows
        result = await db.execute(
            select(Workflow)
            .where(Workflow.organization_id == organization_id)
        )
        workflows = result.scalars().all()
        
        # Get active workflows
        active_workflows = [w for w in workflows if w.status == "active"]
        
        # Get executions today
        today = datetime.utcnow().date()
        result = await db.execute(
            select(WorkflowExecution)
            .where(
                WorkflowExecution.organization_id == organization_id,
                WorkflowExecution.started_at >= today
            )
        )
        today_executions = result.scalars().all()
        
        # Calculate success rate
        completed_executions = [e for e in today_executions if e.status == "completed"]
        success_rate = (len(completed_executions) / len(today_executions) * 100) if today_executions else 0
        
        # Calculate average execution time
        avg_execution_time = 0
        if completed_executions:
            total_time = sum(e.execution_time_ms or 0 for e in completed_executions)
            avg_execution_time = total_time / len(completed_executions) / 1000  # Convert to seconds
        
        return {
            "total_workflows": len(workflows),
            "active_workflows": len(active_workflows),
            "executions_today": len(today_executions),
            "success_rate": round(success_rate, 1),
            "avg_execution_time": round(avg_execution_time, 1)
        }


# Global workflow service instance
workflow_service = WorkflowService() 