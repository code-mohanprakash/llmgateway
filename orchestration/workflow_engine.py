"""
Workflow Engine - Phase 3.1: Multi-Step Workflow Builder

This module provides a sophisticated workflow execution engine that supports:
- Visual workflow design and execution
- Conditional logic and branching
- Parallel execution capabilities
- Error handling and retry mechanisms
- Performance monitoring and optimization
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from enum import Enum
import logging
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Workflow execution status enumeration"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepType(Enum):
    """Workflow step type enumeration"""
    LLM_CALL = "llm_call"
    CONDITION = "condition"
    PARALLEL = "parallel"
    TRANSFORM = "transform"
    DELAY = "delay"
    WEBHOOK = "webhook"


@dataclass
class WorkflowStep:
    """Individual workflow step definition"""
    id: str
    type: StepType
    name: str
    config: Dict[str, Any]
    inputs: List[str] = None
    outputs: List[str] = None
    retry_config: Dict[str, Any] = None
    timeout_seconds: int = 300
    
    def __post_init__(self):
        if self.inputs is None:
            self.inputs = []
        if self.outputs is None:
            self.outputs = []
        if self.retry_config is None:
            self.retry_config = {"max_retries": 3, "backoff_multiplier": 2}


@dataclass
class WorkflowDefinition:
    """Complete workflow definition"""
    id: str
    name: str
    description: str
    version: int
    steps: List[WorkflowStep]
    connections: List[Dict[str, str]]
    variables: Dict[str, Any] = None
    timeout_seconds: int = 3600
    
    def __post_init__(self):
        if self.variables is None:
            self.variables = {}


@dataclass
class ExecutionContext:
    """Workflow execution context"""
    execution_id: str
    workflow_id: str
    organization_id: str
    user_id: str
    input_data: Dict[str, Any]
    variables: Dict[str, Any]
    step_results: Dict[str, Any]
    status: WorkflowStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    total_cost: float = 0.0


class WorkflowEngine:
    """
    Core workflow execution engine with enterprise-grade capabilities.
    
    Supports complex workflow orchestration with conditional logic,
    parallel execution, error handling, and performance monitoring.
    """
    
    def __init__(self, llm_gateway_client=None, audit_logger=None):
        """
        Initialize the workflow engine.
        
        Args:
            llm_gateway_client: Client for making LLM API calls
            audit_logger: Logger for audit trail
        """
        self.llm_client = llm_gateway_client
        self.audit_logger = audit_logger
        self.active_executions: Dict[str, ExecutionContext] = {}
        
    async def execute_workflow(
        self, 
        workflow: WorkflowDefinition, 
        input_data: Dict[str, Any],
        organization_id: str,
        user_id: str
    ) -> ExecutionContext:
        """
        Execute a complete workflow with full orchestration.
        
        Args:
            workflow: Workflow definition to execute
            input_data: Input data for the workflow
            organization_id: Organization executing the workflow
            user_id: User initiating the execution
            
        Returns:
            ExecutionContext: Complete execution context with results
        """
        execution_id = str(uuid.uuid4())
        
        context = ExecutionContext(
            execution_id=execution_id,
            workflow_id=workflow.id,
            organization_id=organization_id,
            user_id=user_id,
            input_data=input_data,
            variables=workflow.variables.copy(),
            step_results={},
            status=WorkflowStatus.DRAFT,
            started_at=datetime.utcnow()
        )
        
        self.active_executions[execution_id] = context
        
        try:
            # Log workflow start
            await self._audit_log(context, "workflow_started", {
                "workflow_name": workflow.name,
                "workflow_version": workflow.version
            })
            
            context.status = WorkflowStatus.ACTIVE
            
            # Execute workflow steps
            await self._execute_workflow_steps(workflow, context)
            
            context.status = WorkflowStatus.COMPLETED
            context.completed_at = datetime.utcnow()
            
            # Log workflow completion
            await self._audit_log(context, "workflow_completed", {
                "execution_time_ms": int((context.completed_at - context.started_at).total_seconds() * 1000),
                "total_cost": context.total_cost
            })
            
        except Exception as e:
            context.status = WorkflowStatus.FAILED
            context.error_message = str(e)
            context.completed_at = datetime.utcnow()
            
            logger.error(f"Workflow execution failed: {execution_id}", exc_info=True)
            
            await self._audit_log(context, "workflow_failed", {
                "error_message": str(e)
            })
            
        finally:
            # Clean up active execution
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
                
        return context
    
    async def _execute_workflow_steps(self, workflow: WorkflowDefinition, context: ExecutionContext):
        """Execute all workflow steps with proper orchestration."""
        
        # Build execution graph
        execution_graph = self._build_execution_graph(workflow)
        
        # Execute steps in topological order
        executed_steps = set()
        
        while len(executed_steps) < len(workflow.steps):
            # Find steps ready for execution
            ready_steps = []
            for step in workflow.steps:
                if (step.id not in executed_steps and 
                    self._are_dependencies_satisfied(step, executed_steps, execution_graph)):
                    ready_steps.append(step)
            
            if not ready_steps:
                raise RuntimeError("Workflow has circular dependencies or unreachable steps")
            
            # Execute ready steps (potentially in parallel)
            await self._execute_step_batch(ready_steps, context)
            
            # Mark steps as executed
            for step in ready_steps:
                executed_steps.add(step.id)
    
    async def _execute_step_batch(self, steps: List[WorkflowStep], context: ExecutionContext):
        """Execute a batch of workflow steps, potentially in parallel."""
        
        if len(steps) == 1:
            # Single step execution
            await self._execute_single_step(steps[0], context)
        else:
            # Parallel execution
            tasks = [self._execute_single_step(step, context) for step in steps]
            await asyncio.gather(*tasks)
    
    async def _execute_single_step(self, step: WorkflowStep, context: ExecutionContext):
        """Execute a single workflow step with error handling and retries."""
        
        step_start_time = datetime.utcnow()
        
        await self._audit_log(context, "step_started", {
            "step_id": step.id,
            "step_name": step.name,
            "step_type": step.type.value
        })
        
        try:
            # Execute step based on type
            if step.type == StepType.LLM_CALL:
                result = await self._execute_llm_step(step, context)
            elif step.type == StepType.CONDITION:
                result = await self._execute_condition_step(step, context)
            elif step.type == StepType.PARALLEL:
                result = await self._execute_parallel_step(step, context)
            elif step.type == StepType.TRANSFORM:
                result = await self._execute_transform_step(step, context)
            elif step.type == StepType.DELAY:
                result = await self._execute_delay_step(step, context)
            elif step.type == StepType.WEBHOOK:
                result = await self._execute_webhook_step(step, context)
            else:
                raise ValueError(f"Unknown step type: {step.type}")
            
            # Store step result
            context.step_results[step.id] = result
            
            # Log step completion
            execution_time = (datetime.utcnow() - step_start_time).total_seconds() * 1000
            await self._audit_log(context, "step_completed", {
                "step_id": step.id,
                "execution_time_ms": int(execution_time),
                "result_size": len(str(result)) if result else 0
            })
            
        except Exception as e:
            logger.error(f"Step execution failed: {step.id}", exc_info=True)
            
            await self._audit_log(context, "step_failed", {
                "step_id": step.id,
                "error_message": str(e)
            })
            
            raise
    
    async def _execute_llm_step(self, step: WorkflowStep, context: ExecutionContext) -> Dict[str, Any]:
        """Execute an LLM API call step."""
        
        if not self.llm_client:
            raise RuntimeError("LLM client not configured")
        
        config = step.config
        prompt = self._resolve_variables(config.get("prompt", ""), context)
        model = config.get("model", "gpt-3.5-turbo")
        provider = config.get("provider", "openai")
        
        # Make LLM call with retry logic
        for attempt in range(step.retry_config.get("max_retries", 3) + 1):
            try:
                response = await self.llm_client.chat_completion(
                    prompt=prompt,
                    model=model,
                    provider=provider,
                    **config.get("parameters", {})
                )
                
                # Track cost
                if "cost" in response:
                    context.total_cost += response["cost"]
                
                return {
                    "response": response.get("response", ""),
                    "model": model,
                    "provider": provider,
                    "tokens": response.get("tokens", {}),
                    "cost": response.get("cost", 0.0),
                    "attempt": attempt + 1
                }
                
            except Exception as e:
                if attempt == step.retry_config.get("max_retries", 3):
                    raise
                
                # Exponential backoff
                backoff_time = step.retry_config.get("backoff_multiplier", 2) ** attempt
                await asyncio.sleep(backoff_time)
                
                logger.warning(f"Step {step.id} attempt {attempt + 1} failed, retrying: {str(e)}")
    
    async def _execute_condition_step(self, step: WorkflowStep, context: ExecutionContext) -> Dict[str, Any]:
        """Execute a conditional logic step."""
        
        condition = step.config.get("condition", "")
        resolved_condition = self._resolve_variables(condition, context)
        
        # Evaluate condition (simple implementation)
        result = eval(resolved_condition)  # Note: In production, use a safer evaluation method
        
        return {
            "condition": condition,
            "resolved_condition": resolved_condition,
            "result": result
        }
    
    async def _execute_parallel_step(self, step: WorkflowStep, context: ExecutionContext) -> Dict[str, Any]:
        """Execute parallel sub-steps."""
        
        sub_steps = step.config.get("sub_steps", [])
        
        # Execute all sub-steps in parallel
        tasks = []
        for sub_step_config in sub_steps:
            sub_step = WorkflowStep(**sub_step_config)
            tasks.append(self._execute_single_step(sub_step, context))
        
        results = await asyncio.gather(*tasks)
        
        return {
            "sub_step_results": results,
            "parallel_execution": True
        }
    
    async def _execute_transform_step(self, step: WorkflowStep, context: ExecutionContext) -> Dict[str, Any]:
        """Execute a data transformation step."""
        
        transformation = step.config.get("transformation", "")
        input_data = self._get_step_input_data(step, context)
        
        # Apply transformation (simplified implementation)
        # In production, this would support more sophisticated transformations
        result = eval(transformation, {"input": input_data, "context": context.variables})
        
        return {
            "transformation": transformation,
            "input_data": input_data,
            "result": result
        }
    
    async def _execute_delay_step(self, step: WorkflowStep, context: ExecutionContext) -> Dict[str, Any]:
        """Execute a delay/wait step."""
        
        delay_seconds = step.config.get("delay_seconds", 1)
        await asyncio.sleep(delay_seconds)
        
        return {
            "delay_seconds": delay_seconds,
            "completed_at": datetime.utcnow().isoformat()
        }
    
    async def _execute_webhook_step(self, step: WorkflowStep, context: ExecutionContext) -> Dict[str, Any]:
        """Execute a webhook call step."""
        
        import aiohttp
        
        url = step.config.get("url", "")
        method = step.config.get("method", "POST")
        headers = step.config.get("headers", {})
        payload = step.config.get("payload", {})
        
        # Resolve variables in payload
        resolved_payload = self._resolve_variables(json.dumps(payload), context)
        
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method=method,
                url=url,
                headers=headers,
                json=json.loads(resolved_payload)
            ) as response:
                result = await response.json()
                
                return {
                    "url": url,
                    "method": method,
                    "status_code": response.status,
                    "response": result
                }
    
    def _build_execution_graph(self, workflow: WorkflowDefinition) -> Dict[str, List[str]]:
        """Build execution dependency graph from workflow connections."""
        
        graph = {step.id: [] for step in workflow.steps}
        
        for connection in workflow.connections:
            from_step = connection.get("from")
            to_step = connection.get("to")
            if from_step and to_step:
                graph[to_step].append(from_step)
        
        return graph
    
    def _are_dependencies_satisfied(
        self, 
        step: WorkflowStep, 
        executed_steps: set, 
        execution_graph: Dict[str, List[str]]
    ) -> bool:
        """Check if all dependencies for a step are satisfied."""
        
        dependencies = execution_graph.get(step.id, [])
        return all(dep_id in executed_steps for dep_id in dependencies)
    
    def _resolve_variables(self, template: str, context: ExecutionContext) -> str:
        """Resolve variables in template strings."""
        
        # Simple variable resolution (in production, use a proper template engine)
        result = template
        
        # Replace context variables
        for key, value in context.variables.items():
            result = result.replace(f"{{{{ {key} }}}}", str(value))
        
        # Replace step results
        for step_id, step_result in context.step_results.items():
            result = result.replace(f"{{{{ {step_id}.result }}}}", str(step_result))
        
        # Replace input data
        for key, value in context.input_data.items():
            result = result.replace(f"{{{{ input.{key} }}}}", str(value))
        
        return result
    
    def _get_step_input_data(self, step: WorkflowStep, context: ExecutionContext) -> Dict[str, Any]:
        """Get input data for a step from previous step results."""
        
        input_data = {}
        
        for input_ref in step.inputs:
            if "." in input_ref:
                step_id, field = input_ref.split(".", 1)
                if step_id in context.step_results:
                    step_result = context.step_results[step_id]
                    if field in step_result:
                        input_data[input_ref] = step_result[field]
            else:
                # Direct reference to step result
                if input_ref in context.step_results:
                    input_data[input_ref] = context.step_results[input_ref]
        
        return input_data
    
    async def _audit_log(self, context: ExecutionContext, action: str, metadata: Dict[str, Any]):
        """Log audit events for workflow execution."""
        
        if self.audit_logger:
            await self.audit_logger.log_event(
                organization_id=context.organization_id,
                user_id=context.user_id,
                action=action,
                resource_type="workflow",
                resource_id=context.workflow_id,
                metadata={
                    "execution_id": context.execution_id,
                    **metadata
                }
            )


class WorkflowExecutor:
    """
    High-level workflow executor with database integration.
    
    Provides enterprise-grade workflow execution with persistence,
    monitoring, and management capabilities.
    """
    
    def __init__(self, db_session, llm_client, audit_logger):
        """
        Initialize the workflow executor.
        
        Args:
            db_session: Database session for persistence
            llm_client: LLM Gateway client
            audit_logger: Audit logging system
        """
        self.db = db_session
        self.engine = WorkflowEngine(llm_client, audit_logger)
        self.audit_logger = audit_logger
    
    async def execute_workflow_by_id(
        self, 
        workflow_id: str, 
        input_data: Dict[str, Any],
        organization_id: str,
        user_id: str
    ) -> str:
        """
        Execute a workflow by ID with full persistence.
        
        Args:
            workflow_id: ID of workflow to execute
            input_data: Input data for execution
            organization_id: Organization ID
            user_id: User ID
            
        Returns:
            str: Execution ID for tracking
        """
        
        # Load workflow definition from database
        workflow_record = await self._get_workflow(workflow_id, organization_id)
        if not workflow_record:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        # Convert database record to workflow definition
        workflow = self._workflow_record_to_definition(workflow_record)
        
        # Create execution record
        execution_id = str(uuid.uuid4())
        execution_record = {
            "id": execution_id,
            "workflow_id": workflow_id,
            "organization_id": organization_id,
            "input_data": input_data,
            "output_data": {},
            "status": WorkflowStatus.DRAFT.value,
            "started_at": datetime.utcnow(),
            "total_cost": 0.0
        }
        
        await self._create_execution_record(execution_record)
        
        try:
            # Execute workflow
            context = await self.engine.execute_workflow(
                workflow, input_data, organization_id, user_id
            )
            
            # Update execution record
            await self._update_execution_record(execution_id, {
                "output_data": context.step_results,
                "status": context.status.value,
                "completed_at": context.completed_at,
                "error_message": context.error_message,
                "total_cost": context.total_cost
            })
            
            return execution_id
            
        except Exception as e:
            # Update execution record with error
            await self._update_execution_record(execution_id, {
                "status": WorkflowStatus.FAILED.value,
                "completed_at": datetime.utcnow(),
                "error_message": str(e)
            })
            
            raise
    
    async def get_execution_status(self, execution_id: str, organization_id: str) -> Dict[str, Any]:
        """Get the status of a workflow execution."""
        
        execution = await self._get_execution(execution_id, organization_id)
        if not execution:
            raise ValueError(f"Execution not found: {execution_id}")
        
        return {
            "execution_id": execution["id"],
            "workflow_id": execution["workflow_id"],
            "status": execution["status"],
            "started_at": execution["started_at"],
            "completed_at": execution.get("completed_at"),
            "total_cost": execution.get("total_cost", 0.0),
            "error_message": execution.get("error_message")
        }
    
    async def list_executions(
        self, 
        organization_id: str, 
        workflow_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List workflow executions for an organization."""
        
        return await self._list_executions(organization_id, workflow_id, limit, offset)
    
    # Database interface methods (to be implemented with actual DB)
    async def _get_workflow(self, workflow_id: str, organization_id: str):
        """Get workflow from database."""
        # Implementation depends on actual database setup
        pass
    
    async def _create_execution_record(self, execution_record: Dict[str, Any]):
        """Create execution record in database."""
        # Implementation depends on actual database setup
        pass
    
    async def _update_execution_record(self, execution_id: str, updates: Dict[str, Any]):
        """Update execution record in database."""
        # Implementation depends on actual database setup
        pass
    
    async def _get_execution(self, execution_id: str, organization_id: str):
        """Get execution record from database."""
        # Implementation depends on actual database setup
        pass
    
    async def _list_executions(
        self, 
        organization_id: str, 
        workflow_id: Optional[str], 
        limit: int, 
        offset: int
    ):
        """List execution records from database."""
        # Implementation depends on actual database setup
        pass
    
    def _workflow_record_to_definition(self, workflow_record) -> WorkflowDefinition:
        """Convert database workflow record to WorkflowDefinition."""
        
        definition_data = workflow_record.get("definition", {})
        
        steps = [WorkflowStep(**step_data) for step_data in definition_data.get("steps", [])]
        
        return WorkflowDefinition(
            id=workflow_record["id"],
            name=workflow_record["name"],
            description=workflow_record.get("description", ""),
            version=workflow_record.get("version", 1),
            steps=steps,
            connections=definition_data.get("connections", []),
            variables=definition_data.get("variables", {}),
            timeout_seconds=definition_data.get("timeout_seconds", 3600)
        )