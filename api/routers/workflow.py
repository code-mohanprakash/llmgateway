"""
Workflow management API endpoints for enterprise orchestration
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime
import json
import uuid

from database.database import get_db
from models.user import User, Organization
from models.rbac import Workflow, WorkflowExecution
from auth.dependencies import get_current_user
from auth.rbac_middleware import require_permission, audit_action

router = APIRouter()


# Pydantic models for API requests/responses
class WorkflowStep(BaseModel):
    id: str
    name: str
    type: str  # 'llm', 'condition', 'loop', 'api_call', 'transform'
    config: Dict[str, Any]
    next_step: Optional[str] = None
    error_step: Optional[str] = None


class WorkflowDefinition(BaseModel):
    name: str
    description: Optional[str] = None
    steps: List[WorkflowStep]
    variables: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None


class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    definition: WorkflowDefinition


class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    definition: Optional[WorkflowDefinition] = None
    status: Optional[str] = None


class WorkflowResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    definition: Dict[str, Any]
    version: int
    status: str
    created_by: str
    created_at: str
    updated_at: str


class WorkflowExecutionRequest(BaseModel):
    input_data: Optional[Dict[str, Any]] = None
    variables: Optional[Dict[str, Any]] = None


class WorkflowExecutionResponse(BaseModel):
    id: str
    workflow_id: str
    status: str
    input_data: Optional[Dict[str, Any]]
    output_data: Optional[Dict[str, Any]]
    started_at: str
    completed_at: Optional[str]
    error_message: Optional[str]
    execution_time_ms: Optional[int]
    total_cost: Optional[float]


# Workflow management endpoints
@router.post("/workflows", response_model=WorkflowResponse)
@require_permission("workflow.create", "workflow")
@audit_action("workflow.create", "workflow")
async def create_workflow(
    workflow_data: WorkflowCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new workflow"""
    organization = current_user.organization
    
    # Check if workflow name already exists in organization
    existing_workflow = await db.execute(
        select(Workflow).where(
            and_(
                Workflow.name == workflow_data.name,
                Workflow.organization_id == organization.id
            )
        )
    )
    
    if existing_workflow.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Workflow with this name already exists in the organization"
        )
    
    # Validate workflow definition
    if not _validate_workflow_definition(workflow_data.definition):
        raise HTTPException(
            status_code=400,
            detail="Invalid workflow definition"
        )
    
    # Create workflow
    workflow = Workflow(
        name=workflow_data.name,
        description=workflow_data.description,
        organization_id=organization.id,
        definition=workflow_data.definition.dict(),
        created_by=current_user.id
    )
    
    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)
    
    return WorkflowResponse(
        id=workflow.id,
        name=workflow.name,
        description=workflow.description,
        definition=workflow.definition,
        version=workflow.version,
        status=workflow.status,
        created_by=workflow.created_by,
        created_at=workflow.created_at,
        updated_at=workflow.updated_at
    )


@router.get("/workflows", response_model=List[WorkflowResponse])
@require_permission("workflow.read", "workflow")
async def list_workflows(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all workflows in the organization"""
    organization = current_user.organization
    
    query = select(Workflow).where(Workflow.organization_id == organization.id)
    
    if status:
        query = query.where(Workflow.status == status)
    
    result = await db.execute(query)
    workflows = result.scalars().all()
    
    return [
        WorkflowResponse(
            id=workflow.id,
            name=workflow.name,
            description=workflow.description,
            definition=workflow.definition,
            version=workflow.version,
            status=workflow.status,
            created_by=workflow.created_by,
            created_at=workflow.created_at,
            updated_at=workflow.updated_at
        )
        for workflow in workflows
    ]


@router.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
@require_permission("workflow.read", "workflow")
async def get_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific workflow"""
    organization = current_user.organization
    
    result = await db.execute(
        select(Workflow).where(
            and_(
                Workflow.id == workflow_id,
                Workflow.organization_id == organization.id
            )
        )
    )
    
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return WorkflowResponse(
        id=workflow.id,
        name=workflow.name,
        description=workflow.description,
        definition=workflow.definition,
        version=workflow.version,
        status=workflow.status,
        created_by=workflow.created_by,
        created_at=workflow.created_at,
        updated_at=workflow.updated_at
    )


@router.put("/workflows/{workflow_id}", response_model=WorkflowResponse)
@require_permission("workflow.update", "workflow")
@audit_action("workflow.update", "workflow")
async def update_workflow(
    workflow_id: str,
    workflow_data: WorkflowUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a workflow"""
    organization = current_user.organization
    
    result = await db.execute(
        select(Workflow).where(
            and_(
                Workflow.id == workflow_id,
                Workflow.organization_id == organization.id
            )
        )
    )
    
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Update fields
    if workflow_data.name is not None:
        workflow.name = workflow_data.name
    if workflow_data.description is not None:
        workflow.description = workflow_data.description
    if workflow_data.definition is not None:
        # Validate workflow definition
        if not _validate_workflow_definition(workflow_data.definition):
            raise HTTPException(
                status_code=400,
                detail="Invalid workflow definition"
            )
        workflow.definition = workflow_data.definition.dict()
        workflow.version += 1
    if workflow_data.status is not None:
        workflow.status = workflow_data.status
    
    await db.commit()
    await db.refresh(workflow)
    
    return WorkflowResponse(
        id=workflow.id,
        name=workflow.name,
        description=workflow.description,
        definition=workflow.definition,
        version=workflow.version,
        status=workflow.status,
        created_by=workflow.created_by,
        created_at=workflow.created_at,
        updated_at=workflow.updated_at
    )


@router.delete("/workflows/{workflow_id}")
@require_permission("workflow.delete", "workflow")
@audit_action("workflow.delete", "workflow")
async def delete_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a workflow"""
    organization = current_user.organization
    
    result = await db.execute(
        select(Workflow).where(
            and_(
                Workflow.id == workflow_id,
                Workflow.organization_id == organization.id
            )
        )
    )
    
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Check if workflow has active executions
    active_executions = await db.execute(
        select(WorkflowExecution).where(
            and_(
                WorkflowExecution.workflow_id == workflow_id,
                WorkflowExecution.status.in_(['running', 'pending'])
            )
        )
    )
    
    if active_executions.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Cannot delete workflow with active executions"
        )
    
    await db.delete(workflow)
    await db.commit()
    
    return {"message": "Workflow deleted successfully"}


# Workflow execution endpoints
@router.post("/workflows/{workflow_id}/execute", response_model=WorkflowExecutionResponse)
@require_permission("workflow.execute", "workflow")
@audit_action("workflow.execute", "workflow_execution")
async def execute_workflow(
    workflow_id: str,
    execution_request: WorkflowExecutionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Execute a workflow"""
    organization = current_user.organization
    
    # Get workflow
    result = await db.execute(
        select(Workflow).where(
            and_(
                Workflow.id == workflow_id,
                Workflow.organization_id == organization.id
            )
        )
    )
    
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    if workflow.status != 'active':
        raise HTTPException(
            status_code=400,
            detail="Workflow is not active"
        )
    
    # Create execution record
    execution = WorkflowExecution(
        workflow_id=workflow_id,
        organization_id=organization.id,
        input_data=execution_request.input_data,
        status='running'
    )
    
    db.add(execution)
    await db.commit()
    await db.refresh(execution)
    
    # Start execution in background
    background_tasks.add_task(
        _execute_workflow_background,
        execution.id,
        workflow.definition,
        execution_request.input_data,
        execution_request.variables,
        organization.id
    )
    
    return WorkflowExecutionResponse(
        id=execution.id,
        workflow_id=execution.workflow_id,
        status=execution.status,
        input_data=execution.input_data,
        output_data=execution.output_data,
        started_at=execution.started_at,
        completed_at=execution.completed_at,
        error_message=execution.error_message,
        execution_time_ms=execution.execution_time_ms,
        total_cost=execution.total_cost
    )


@router.get("/workflows/{workflow_id}/executions", response_model=List[WorkflowExecutionResponse])
@require_permission("workflow.read", "workflow")
async def list_workflow_executions(
    workflow_id: str,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List executions for a workflow"""
    organization = current_user.organization
    
    # Verify workflow exists and belongs to organization
    workflow_result = await db.execute(
        select(Workflow).where(
            and_(
                Workflow.id == workflow_id,
                Workflow.organization_id == organization.id
            )
        )
    )
    
    if not workflow_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Get executions
    query = select(WorkflowExecution).where(
        WorkflowExecution.workflow_id == workflow_id
    )
    
    if status:
        query = query.where(WorkflowExecution.status == status)
    
    query = query.order_by(WorkflowExecution.started_at.desc())
    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    executions = result.scalars().all()
    
    return [
        WorkflowExecutionResponse(
            id=execution.id,
            workflow_id=execution.workflow_id,
            status=execution.status,
            input_data=execution.input_data,
            output_data=execution.output_data,
            started_at=execution.started_at,
            completed_at=execution.completed_at,
            error_message=execution.error_message,
            execution_time_ms=execution.execution_time_ms,
            total_cost=execution.total_cost
        )
        for execution in executions
    ]


@router.get("/executions/{execution_id}", response_model=WorkflowExecutionResponse)
@require_permission("workflow.read", "workflow")
async def get_workflow_execution(
    execution_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific workflow execution"""
    organization = current_user.organization
    
    result = await db.execute(
        select(WorkflowExecution).where(
            and_(
                WorkflowExecution.id == execution_id,
                WorkflowExecution.organization_id == organization.id
            )
        )
    )
    
    execution = result.scalar_one_or_none()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Workflow execution not found")
    
    return WorkflowExecutionResponse(
        id=execution.id,
        workflow_id=execution.workflow_id,
        status=execution.status,
        input_data=execution.input_data,
        output_data=execution.output_data,
        started_at=execution.started_at,
        completed_at=execution.completed_at,
        error_message=execution.error_message,
        execution_time_ms=execution.execution_time_ms,
        total_cost=execution.total_cost
    )


# Utility functions
def _validate_workflow_definition(definition: WorkflowDefinition) -> bool:
    """Validate workflow definition"""
    if not definition.steps:
        return False
    
    # Check for circular references
    step_ids = {step.id for step in definition.steps}
    for step in definition.steps:
        if step.next_step and step.next_step not in step_ids:
            return False
        if step.error_step and step.error_step not in step_ids:
            return False
    
    # Check for valid step types
    valid_types = ['llm', 'condition', 'loop', 'api_call', 'transform']
    for step in definition.steps:
        if step.type not in valid_types:
            return False
    
    return True


async def _execute_workflow_background(
    execution_id: str,
    workflow_definition: Dict[str, Any],
    input_data: Optional[Dict[str, Any]],
    variables: Optional[Dict[str, Any]],
    organization_id: str
):
    """Execute workflow in background"""
    from database.database import get_db
    
    async for db in get_db():
        try:
            # Get execution record
            result = await db.execute(
                select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
            )
            execution = result.scalar_one_or_none()
            
            if not execution:
                return
            
            start_time = datetime.utcnow()
            total_cost = 0.0
            current_data = input_data or {}
            workflow_vars = variables or {}
            
            # Execute workflow steps
            steps = workflow_definition.get('steps', [])
            step_map = {step['id']: step for step in steps}
            
            current_step_id = steps[0]['id'] if steps else None
            
            while current_step_id and current_step_id in step_map:
                step = step_map[current_step_id]
                
                try:
                    # Execute step based on type
                    step_result = await _execute_step(
                        step, current_data, workflow_vars, organization_id
                    )
                    
                    # Update data and variables
                    if step_result.get('output'):
                        current_data.update(step_result['output'])
                    if step_result.get('variables'):
                        workflow_vars.update(step_result['variables'])
                    
                    # Add cost
                    total_cost += step_result.get('cost', 0.0)
                    
                    # Determine next step
                    if step_result.get('success', True):
                        current_step_id = step.get('next_step')
                    else:
                        current_step_id = step.get('error_step')
                        
                except Exception as e:
                    # Step failed, go to error step
                    current_step_id = step.get('error_step')
                    if not current_step_id:
                        # No error step, workflow fails
                        break
            
            # Update execution record
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            execution.status = 'completed'
            execution.completed_at = datetime.utcnow()
            execution.output_data = current_data
            execution.execution_time_ms = int(execution_time)
            execution.total_cost = total_cost
            
            await db.commit()
            
        except Exception as e:
            # Update execution record with error
            execution.status = 'failed'
            execution.completed_at = datetime.utcnow()
            execution.error_message = str(e)
            await db.commit()


async def _execute_step(
    step: Dict[str, Any],
    current_data: Dict[str, Any],
    workflow_vars: Dict[str, Any],
    organization_id: str
) -> Dict[str, Any]:
    """Execute a single workflow step"""
    step_type = step.get('type')
    config = step.get('config', {})
    
    if step_type == 'llm':
        return await _execute_llm_step(config, current_data, workflow_vars, organization_id)
    elif step_type == 'condition':
        return await _execute_condition_step(config, current_data, workflow_vars)
    elif step_type == 'loop':
        return await _execute_loop_step(config, current_data, workflow_vars, organization_id)
    elif step_type == 'api_call':
        return await _execute_api_call_step(config, current_data, workflow_vars)
    elif step_type == 'transform':
        return await _execute_transform_step(config, current_data, workflow_vars)
    else:
        raise ValueError(f"Unknown step type: {step_type}")


async def _execute_llm_step(
    config: Dict[str, Any],
    current_data: Dict[str, Any],
    workflow_vars: Dict[str, Any],
    organization_id: str
) -> Dict[str, Any]:
    """Execute LLM step"""
    from api.routers.llm import generate_text
    
    # Prepare prompt with variable substitution
    prompt = config.get('prompt', '')
    for var_name, var_value in workflow_vars.items():
        prompt = prompt.replace(f"{{{{{var_name}}}}}", str(var_value))
    
    # Call LLM API
    response = await generate_text(
        prompt=prompt,
        model=config.get('model', 'gpt-3.5-turbo'),
        max_tokens=config.get('max_tokens', 1000),
        temperature=config.get('temperature', 0.7),
        organization_id=organization_id
    )
    
    return {
        'success': True,
        'output': {config.get('output_key', 'result'): response.get('text', '')},
        'cost': response.get('cost', 0.0)
    }


async def _execute_condition_step(
    config: Dict[str, Any],
    current_data: Dict[str, Any],
    workflow_vars: Dict[str, Any]
) -> Dict[str, Any]:
    """Execute condition step"""
    condition = config.get('condition', '')
    
    # Evaluate condition
    try:
        # Simple condition evaluation (in production, use a safe expression evaluator)
        result = eval(condition, {"__builtins__": {}}, {
            **current_data,
            **workflow_vars
        })
        
        return {
            'success': True,
            'output': {'condition_result': result}
        }
    except Exception as e:
        return {
            'success': False,
            'output': {'condition_result': False}
        }


async def _execute_loop_step(
    config: Dict[str, Any],
    current_data: Dict[str, Any],
    workflow_vars: Dict[str, Any],
    organization_id: str
) -> Dict[str, Any]:
    """Execute loop step"""
    items = config.get('items', [])
    loop_steps = config.get('steps', [])
    
    results = []
    
    for item in items:
        # Execute loop steps for each item
        loop_data = {**current_data, 'item': item}
        loop_vars = {**workflow_vars, 'item': item}
        
        for step in loop_steps:
            step_result = await _execute_step(step, loop_data, loop_vars, organization_id)
            if step_result.get('output'):
                loop_data.update(step_result['output'])
        
        results.append(loop_data)
    
    return {
        'success': True,
        'output': {config.get('output_key', 'loop_results'): results}
    }


async def _execute_api_call_step(
    config: Dict[str, Any],
    current_data: Dict[str, Any],
    workflow_vars: Dict[str, Any]
) -> Dict[str, Any]:
    """Execute API call step"""
    import httpx
    
    url = config.get('url', '')
    method = config.get('method', 'GET')
    headers = config.get('headers', {})
    body = config.get('body', {})
    
    # Substitute variables in URL and body
    for var_name, var_value in {**current_data, **workflow_vars}.items():
        url = url.replace(f"{{{{{var_name}}}}}", str(var_value))
        if isinstance(body, dict):
            for key, value in body.items():
                if isinstance(value, str):
                    body[key] = value.replace(f"{{{{{var_name}}}}}", str(var_value))
    
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=method,
            url=url,
            headers=headers,
            json=body if method in ['POST', 'PUT', 'PATCH'] else None
        )
        
        return {
            'success': response.status_code < 400,
            'output': {
                'status_code': response.status_code,
                'response': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            }
        }


async def _execute_transform_step(
    config: Dict[str, Any],
    current_data: Dict[str, Any],
    workflow_vars: Dict[str, Any]
) -> Dict[str, Any]:
    """Execute transform step"""
    transform_type = config.get('type', 'map')
    
    if transform_type == 'map':
        # Map transformation
        mapping = config.get('mapping', {})
        result = {}
        
        for output_key, input_key in mapping.items():
            if input_key in current_data:
                result[output_key] = current_data[input_key]
            elif input_key in workflow_vars:
                result[output_key] = workflow_vars[input_key]
        
        return {
            'success': True,
            'output': result
        }
    
    elif transform_type == 'filter':
        # Filter transformation
        filter_key = config.get('key')
        filter_value = config.get('value')
        
        if isinstance(current_data, list):
            filtered = [
                item for item in current_data
                if item.get(filter_key) == filter_value
            ]
            return {
                'success': True,
                'output': {config.get('output_key', 'filtered'): filtered}
            }
    
    elif transform_type == 'join':
        # Join transformation
        separator = config.get('separator', ' ')
        keys = config.get('keys', [])
        
        values = []
        for key in keys:
            if key in current_data:
                values.append(str(current_data[key]))
            elif key in workflow_vars:
                values.append(str(workflow_vars[key]))
        
        joined = separator.join(values)
        return {
            'success': True,
            'output': {config.get('output_key', 'joined'): joined}
        }
    
    return {
        'success': True,
        'output': {}
    } 