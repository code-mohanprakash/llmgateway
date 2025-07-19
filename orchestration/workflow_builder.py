"""
Workflow Builder - Visual Workflow Design Components

This module provides components for the visual workflow builder:
- Workflow validation and optimization
- Step dependency analysis
- Template management
- Export and import functionality
"""

import json
import uuid
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
import logging

from .workflow_engine import WorkflowDefinition, WorkflowStep, StepType

logger = logging.getLogger(__name__)


@dataclass
class ValidationError:
    """Workflow validation error"""
    step_id: Optional[str]
    error_type: str
    message: str
    severity: str  # 'error', 'warning', 'info'


@dataclass
class WorkflowTemplate:
    """Predefined workflow template"""
    id: str
    name: str
    description: str
    category: str
    tags: List[str]
    definition: WorkflowDefinition
    use_cases: List[str]
    estimated_cost_per_run: float


class WorkflowValidator:
    """
    Workflow validation engine for ensuring workflow correctness.
    
    Validates:
    - Step dependencies and connections
    - Circular dependency detection
    - Variable reference validation
    - Resource availability
    - Performance optimization suggestions
    """
    
    def __init__(self):
        """Initialize the workflow validator."""
        self.validation_rules = []
    
    def validate_workflow(self, workflow: WorkflowDefinition) -> List[ValidationError]:
        """
        Perform comprehensive workflow validation.
        
        Args:
            workflow: Workflow definition to validate
            
        Returns:
            List[ValidationError]: List of validation errors and warnings
        """
        
        errors = []
        
        # Basic structure validation
        errors.extend(self._validate_basic_structure(workflow))
        
        # Dependency validation
        errors.extend(self._validate_dependencies(workflow))
        
        # Variable validation
        errors.extend(self._validate_variables(workflow))
        
        # Performance validation
        errors.extend(self._validate_performance(workflow))
        
        # Security validation
        errors.extend(self._validate_security(workflow))
        
        return errors
    
    def _validate_basic_structure(self, workflow: WorkflowDefinition) -> List[ValidationError]:
        """Validate basic workflow structure."""
        
        errors = []
        
        # Check for empty workflow
        if not workflow.steps:
            errors.append(ValidationError(
                step_id=None,
                error_type="empty_workflow",
                message="Workflow must contain at least one step",
                severity="error"
            ))
            return errors
        
        # Check for duplicate step IDs
        step_ids = [step.id for step in workflow.steps]
        duplicate_ids = set([id for id in step_ids if step_ids.count(id) > 1])
        
        for duplicate_id in duplicate_ids:
            errors.append(ValidationError(
                step_id=duplicate_id,
                error_type="duplicate_step_id",
                message=f"Duplicate step ID found: {duplicate_id}",
                severity="error"
            ))
        
        # Validate individual steps
        for step in workflow.steps:
            errors.extend(self._validate_step(step))
        
        return errors
    
    def _validate_step(self, step: WorkflowStep) -> List[ValidationError]:
        """Validate individual step configuration."""
        
        errors = []
        
        # Check required fields
        if not step.name:
            errors.append(ValidationError(
                step_id=step.id,
                error_type="missing_name",
                message="Step name is required",
                severity="error"
            ))
        
        # Validate step type specific configuration
        if step.type == StepType.LLM_CALL:
            errors.extend(self._validate_llm_step(step))
        elif step.type == StepType.CONDITION:
            errors.extend(self._validate_condition_step(step))
        elif step.type == StepType.WEBHOOK:
            errors.extend(self._validate_webhook_step(step))
        
        # Validate timeout
        if step.timeout_seconds <= 0:
            errors.append(ValidationError(
                step_id=step.id,
                error_type="invalid_timeout",
                message="Timeout must be greater than 0",
                severity="error"
            ))
        
        return errors
    
    def _validate_llm_step(self, step: WorkflowStep) -> List[ValidationError]:
        """Validate LLM call step configuration."""
        
        errors = []
        
        if "prompt" not in step.config:
            errors.append(ValidationError(
                step_id=step.id,
                error_type="missing_prompt",
                message="LLM step requires a prompt",
                severity="error"
            ))
        
        if "model" not in step.config:
            errors.append(ValidationError(
                step_id=step.id,
                error_type="missing_model",
                message="LLM step requires a model specification",
                severity="error"
            ))
        
        # Validate prompt template variables
        prompt = step.config.get("prompt", "")
        variables = self._extract_template_variables(prompt)
        
        for variable in variables:
            if not self._is_valid_variable_reference(variable, step):
                errors.append(ValidationError(
                    step_id=step.id,
                    error_type="invalid_variable",
                    message=f"Invalid variable reference: {variable}",
                    severity="warning"
                ))
        
        return errors
    
    def _validate_condition_step(self, step: WorkflowStep) -> List[ValidationError]:
        """Validate condition step configuration."""
        
        errors = []
        
        if "condition" not in step.config:
            errors.append(ValidationError(
                step_id=step.id,
                error_type="missing_condition",
                message="Condition step requires a condition expression",
                severity="error"
            ))
        
        # Validate condition syntax (basic check)
        condition = step.config.get("condition", "")
        if not self._is_valid_condition_syntax(condition):
            errors.append(ValidationError(
                step_id=step.id,
                error_type="invalid_condition",
                message="Invalid condition syntax",
                severity="error"
            ))
        
        return errors
    
    def _validate_webhook_step(self, step: WorkflowStep) -> List[ValidationError]:
        """Validate webhook step configuration."""
        
        errors = []
        
        if "url" not in step.config:
            errors.append(ValidationError(
                step_id=step.id,
                error_type="missing_url",
                message="Webhook step requires a URL",
                severity="error"
            ))
        
        # Validate URL format
        url = step.config.get("url", "")
        if not self._is_valid_url(url):
            errors.append(ValidationError(
                step_id=step.id,
                error_type="invalid_url",
                message="Invalid URL format",
                severity="error"
            ))
        
        return errors
    
    def _validate_dependencies(self, workflow: WorkflowDefinition) -> List[ValidationError]:
        """Validate step dependencies and detect cycles."""
        
        errors = []
        
        # Build dependency graph
        dependencies = {}
        for connection in workflow.connections:
            from_step = connection.get("from")
            to_step = connection.get("to")
            
            if to_step not in dependencies:
                dependencies[to_step] = []
            dependencies[to_step].append(from_step)
        
        # Check for circular dependencies
        cycles = self._detect_cycles(dependencies)
        for cycle in cycles:
            errors.append(ValidationError(
                step_id=None,
                error_type="circular_dependency",
                message=f"Circular dependency detected: {' -> '.join(cycle)}",
                severity="error"
            ))
        
        # Check for unreachable steps
        reachable_steps = self._find_reachable_steps(workflow)
        all_step_ids = {step.id for step in workflow.steps}
        unreachable_steps = all_step_ids - reachable_steps
        
        for step_id in unreachable_steps:
            errors.append(ValidationError(
                step_id=step_id,
                error_type="unreachable_step",
                message="Step is not reachable from any entry point",
                severity="warning"
            ))
        
        return errors
    
    def _validate_variables(self, workflow: WorkflowDefinition) -> List[ValidationError]:
        """Validate variable references throughout the workflow."""
        
        errors = []
        
        # Collect all variable definitions
        defined_variables = set(workflow.variables.keys())
        
        # Add step outputs as available variables
        for step in workflow.steps:
            for output in step.outputs:
                defined_variables.add(f"{step.id}.{output}")
        
        # Check variable references in each step
        for step in workflow.steps:
            # Check prompt templates
            if step.type == StepType.LLM_CALL and "prompt" in step.config:
                variables = self._extract_template_variables(step.config["prompt"])
                for variable in variables:
                    if variable not in defined_variables:
                        errors.append(ValidationError(
                            step_id=step.id,
                            error_type="undefined_variable",
                            message=f"Undefined variable: {variable}",
                            severity="error"
                        ))
        
        return errors
    
    def _validate_performance(self, workflow: WorkflowDefinition) -> List[ValidationError]:
        """Validate workflow performance characteristics."""
        
        errors = []
        
        # Check for excessive timeout values
        for step in workflow.steps:
            if step.timeout_seconds > 3600:  # 1 hour
                errors.append(ValidationError(
                    step_id=step.id,
                    error_type="excessive_timeout",
                    message="Step timeout exceeds recommended maximum (1 hour)",
                    severity="warning"
                ))
        
        # Check for potential parallelization opportunities
        sequential_llm_steps = self._find_sequential_llm_steps(workflow)
        if len(sequential_llm_steps) > 1:
            errors.append(ValidationError(
                step_id=None,
                error_type="parallelization_opportunity",
                message=f"Consider parallelizing independent LLM steps: {', '.join(sequential_llm_steps)}",
                severity="info"
            ))
        
        return errors
    
    def _validate_security(self, workflow: WorkflowDefinition) -> List[ValidationError]:
        """Validate workflow security considerations."""
        
        errors = []
        
        # Check for hardcoded secrets
        for step in workflow.steps:
            config_str = json.dumps(step.config)
            if self._contains_potential_secrets(config_str):
                errors.append(ValidationError(
                    step_id=step.id,
                    error_type="potential_secret",
                    message="Step configuration may contain hardcoded secrets",
                    severity="warning"
                ))
        
        return errors
    
    def _extract_template_variables(self, template: str) -> Set[str]:
        """Extract variable references from template string."""
        
        import re
        
        # Find patterns like {{ variable_name }}
        pattern = r'\{\{\s*([^}]+)\s*\}\}'
        matches = re.findall(pattern, template)
        
        return set(match.strip() for match in matches)
    
    def _is_valid_variable_reference(self, variable: str, step: WorkflowStep) -> bool:
        """Check if variable reference is valid."""
        
        # Basic validation - in production, this would be more sophisticated
        return bool(variable and not variable.startswith('__'))
    
    def _is_valid_condition_syntax(self, condition: str) -> bool:
        """Validate condition syntax."""
        
        # Basic syntax check - in production, use proper expression parser
        try:
            # Test compilation (don't execute)
            compile(condition, '<string>', 'eval')
            return True
        except SyntaxError:
            return False
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format."""
        
        import re
        
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return bool(url_pattern.match(url))
    
    def _detect_cycles(self, dependencies: Dict[str, List[str]]) -> List[List[str]]:
        """Detect circular dependencies in workflow."""
        
        def dfs(node, path, visited):
            if node in path:
                # Found cycle
                cycle_start = path.index(node)
                return [path[cycle_start:] + [node]]
            
            if node in visited:
                return []
            
            visited.add(node)
            path.append(node)
            
            cycles = []
            for dependency in dependencies.get(node, []):
                cycles.extend(dfs(dependency, path[:], visited))
            
            return cycles
        
        all_cycles = []
        visited = set()
        
        for node in dependencies:
            if node not in visited:
                all_cycles.extend(dfs(node, [], visited))
        
        return all_cycles
    
    def _find_reachable_steps(self, workflow: WorkflowDefinition) -> Set[str]:
        """Find all reachable steps in workflow."""
        
        # Build forward dependency graph
        dependencies = {}
        for connection in workflow.connections:
            from_step = connection.get("from")
            to_step = connection.get("to")
            
            if from_step not in dependencies:
                dependencies[from_step] = []
            dependencies[from_step].append(to_step)
        
        # Find entry points (steps with no incoming connections)
        all_step_ids = {step.id for step in workflow.steps}
        incoming_steps = set()
        for targets in dependencies.values():
            incoming_steps.update(targets)
        
        entry_points = all_step_ids - incoming_steps
        
        # Traverse from entry points
        reachable = set()
        to_visit = list(entry_points)
        
        while to_visit:
            current = to_visit.pop()
            if current not in reachable:
                reachable.add(current)
                to_visit.extend(dependencies.get(current, []))
        
        return reachable
    
    def _find_sequential_llm_steps(self, workflow: WorkflowDefinition) -> List[str]:
        """Find LLM steps that could potentially be parallelized."""
        
        llm_steps = [step.id for step in workflow.steps if step.type == StepType.LLM_CALL]
        
        # Simple heuristic: find LLM steps with no dependencies between them
        # In practice, this would be more sophisticated
        
        return llm_steps
    
    def _contains_potential_secrets(self, text: str) -> bool:
        """Check if text contains potential secrets."""
        
        import re
        
        # Simple patterns for common secret formats
        secret_patterns = [
            r'(?i)(password|pwd|secret|key|token)\s*[:=]\s*["\']?[a-zA-Z0-9+/]{8,}["\']?',
            r'["\'][a-zA-Z0-9+/]{32,}["\']',  # Base64-like strings
            r'sk-[a-zA-Z0-9]{32,}',  # OpenAI-style keys
        ]
        
        for pattern in secret_patterns:
            if re.search(pattern, text):
                return True
        
        return False


class WorkflowBuilder:
    """
    High-level workflow builder with template management.
    
    Provides:
    - Workflow creation and editing
    - Template management
    - Import/export functionality
    - Optimization suggestions
    """
    
    def __init__(self):
        """Initialize the workflow builder."""
        self.validator = WorkflowValidator()
        self.templates = self._load_default_templates()
    
    def create_workflow_from_template(
        self, 
        template_id: str, 
        customizations: Dict[str, Any] = None
    ) -> WorkflowDefinition:
        """
        Create a workflow from a template.
        
        Args:
            template_id: Template identifier
            customizations: Optional customizations to apply
            
        Returns:
            WorkflowDefinition: Created workflow
        """
        
        template = self._get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        # Clone template definition
        workflow = WorkflowDefinition(
            id=str(uuid.uuid4()),
            name=template.definition.name,
            description=template.definition.description,
            version=1,
            steps=template.definition.steps[:],  # Copy steps
            connections=template.definition.connections[:],  # Copy connections
            variables=template.definition.variables.copy(),  # Copy variables
            timeout_seconds=template.definition.timeout_seconds
        )
        
        # Apply customizations
        if customizations:
            workflow = self._apply_customizations(workflow, customizations)
        
        return workflow
    
    def optimize_workflow(self, workflow: WorkflowDefinition) -> WorkflowDefinition:
        """
        Optimize workflow for performance and cost.
        
        Args:
            workflow: Workflow to optimize
            
        Returns:
            WorkflowDefinition: Optimized workflow
        """
        
        optimized = workflow
        
        # Apply optimization techniques
        optimized = self._optimize_parallelization(optimized)
        optimized = self._optimize_caching(optimized)
        optimized = self._optimize_timeouts(optimized)
        
        return optimized
    
    def export_workflow(self, workflow: WorkflowDefinition, format: str = "json") -> str:
        """
        Export workflow definition.
        
        Args:
            workflow: Workflow to export
            format: Export format ('json', 'yaml')
            
        Returns:
            str: Exported workflow
        """
        
        if format.lower() == "json":
            return json.dumps(asdict(workflow), indent=2)
        elif format.lower() == "yaml":
            import yaml
            return yaml.dump(asdict(workflow), default_flow_style=False)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def import_workflow(self, data: str, format: str = "json") -> WorkflowDefinition:
        """
        Import workflow definition.
        
        Args:
            data: Workflow data
            format: Import format ('json', 'yaml')
            
        Returns:
            WorkflowDefinition: Imported workflow
        """
        
        if format.lower() == "json":
            workflow_dict = json.loads(data)
        elif format.lower() == "yaml":
            import yaml
            workflow_dict = yaml.safe_load(data)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        # Convert to WorkflowDefinition
        steps = [WorkflowStep(**step) for step in workflow_dict.get("steps", [])]
        
        workflow = WorkflowDefinition(
            id=workflow_dict.get("id", str(uuid.uuid4())),
            name=workflow_dict["name"],
            description=workflow_dict.get("description", ""),
            version=workflow_dict.get("version", 1),
            steps=steps,
            connections=workflow_dict.get("connections", []),
            variables=workflow_dict.get("variables", {}),
            timeout_seconds=workflow_dict.get("timeout_seconds", 3600)
        )
        
        return workflow
    
    def get_available_templates(self) -> List[WorkflowTemplate]:
        """Get list of available workflow templates."""
        return list(self.templates.values())
    
    def _load_default_templates(self) -> Dict[str, WorkflowTemplate]:
        """Load default workflow templates."""
        
        templates = {}
        
        # Simple LLM Call Template
        simple_llm = WorkflowTemplate(
            id="simple_llm",
            name="Simple LLM Call",
            description="Basic workflow with a single LLM call",
            category="Basic",
            tags=["llm", "simple", "beginner"],
            definition=self._create_simple_llm_template(),
            use_cases=["Quick text generation", "Single model inference", "API testing"],
            estimated_cost_per_run=0.05
        )
        templates[simple_llm.id] = simple_llm
        
        # Model Comparison Template
        comparison = WorkflowTemplate(
            id="model_comparison",
            name="Model Comparison",
            description="Compare responses from multiple models",
            category="Analysis",
            tags=["comparison", "analysis", "multiple-models"],
            definition=self._create_model_comparison_template(),
            use_cases=["Model evaluation", "Quality comparison", "A/B testing"],
            estimated_cost_per_run=0.20
        )
        templates[comparison.id] = comparison
        
        return templates
    
    def _create_simple_llm_template(self) -> WorkflowDefinition:
        """Create simple LLM call template."""
        
        step = WorkflowStep(
            id="llm_call",
            type=StepType.LLM_CALL,
            name="LLM Call",
            config={
                "prompt": "{{ input.prompt }}",
                "model": "gpt-3.5-turbo",
                "provider": "openai",
                "parameters": {
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            },
            outputs=["response", "tokens", "cost"]
        )
        
        return WorkflowDefinition(
            id="simple_llm_template",
            name="Simple LLM Call",
            description="Basic LLM call workflow",
            version=1,
            steps=[step],
            connections=[],
            variables={
                "default_temperature": 0.7
            }
        )
    
    def _create_model_comparison_template(self) -> WorkflowDefinition:
        """Create model comparison template."""
        
        gpt_step = WorkflowStep(
            id="gpt_call",
            type=StepType.LLM_CALL,
            name="GPT Call",
            config={
                "prompt": "{{ input.prompt }}",
                "model": "gpt-3.5-turbo",
                "provider": "openai",
                "parameters": {"temperature": 0.7}
            },
            outputs=["response", "tokens", "cost"]
        )
        
        claude_step = WorkflowStep(
            id="claude_call",
            type=StepType.LLM_CALL,
            name="Claude Call",
            config={
                "prompt": "{{ input.prompt }}",
                "model": "claude-3-sonnet",
                "provider": "anthropic",
                "parameters": {"temperature": 0.7}
            },
            outputs=["response", "tokens", "cost"]
        )
        
        comparison_step = WorkflowStep(
            id="compare_results",
            type=StepType.TRANSFORM,
            name="Compare Results",
            config={
                "transformation": "{'gpt_response': gpt_call.response, 'claude_response': claude_call.response, 'cost_comparison': {'gpt': gpt_call.cost, 'claude': claude_call.cost}}"
            },
            inputs=["gpt_call.response", "claude_call.response", "gpt_call.cost", "claude_call.cost"],
            outputs=["comparison_result"]
        )
        
        return WorkflowDefinition(
            id="model_comparison_template",
            name="Model Comparison",
            description="Compare responses from GPT and Claude",
            version=1,
            steps=[gpt_step, claude_step, comparison_step],
            connections=[
                {"from": "gpt_call", "to": "compare_results"},
                {"from": "claude_call", "to": "compare_results"}
            ],
            variables={}
        )
    
    def _get_template(self, template_id: str) -> Optional[WorkflowTemplate]:
        """Get template by ID."""
        return self.templates.get(template_id)
    
    def _apply_customizations(
        self, 
        workflow: WorkflowDefinition, 
        customizations: Dict[str, Any]
    ) -> WorkflowDefinition:
        """Apply customizations to workflow."""
        
        # Apply name and description changes
        if "name" in customizations:
            workflow.name = customizations["name"]
        
        if "description" in customizations:
            workflow.description = customizations["description"]
        
        # Apply variable changes
        if "variables" in customizations:
            workflow.variables.update(customizations["variables"])
        
        # Apply step customizations
        if "steps" in customizations:
            for step_customization in customizations["steps"]:
                step_id = step_customization.get("id")
                step = next((s for s in workflow.steps if s.id == step_id), None)
                
                if step:
                    if "config" in step_customization:
                        step.config.update(step_customization["config"])
        
        return workflow
    
    def _optimize_parallelization(self, workflow: WorkflowDefinition) -> WorkflowDefinition:
        """Optimize workflow for parallel execution."""
        
        # Identify independent LLM steps that can run in parallel
        # This is a simplified implementation
        
        llm_steps = [step for step in workflow.steps if step.type == StepType.LLM_CALL]
        
        # If we have multiple independent LLM steps, consider wrapping them in a parallel step
        if len(llm_steps) > 1:
            # Check if they're actually independent
            dependent_steps = set()
            for connection in workflow.connections:
                from_step = connection.get("from")
                to_step = connection.get("to")
                if from_step in [s.id for s in llm_steps] and to_step in [s.id for s in llm_steps]:
                    dependent_steps.update([from_step, to_step])
            
            independent_llm_steps = [s for s in llm_steps if s.id not in dependent_steps]
            
            if len(independent_llm_steps) > 1:
                logger.info(f"Found {len(independent_llm_steps)} independent LLM steps that could be parallelized")
        
        return workflow
    
    def _optimize_caching(self, workflow: WorkflowDefinition) -> WorkflowDefinition:
        """Optimize workflow for caching."""
        
        # Add caching hints to deterministic steps
        for step in workflow.steps:
            if step.type == StepType.LLM_CALL:
                # If temperature is 0, this is deterministic and can be cached
                temperature = step.config.get("parameters", {}).get("temperature", 0.7)
                if temperature == 0:
                    step.config["cache_enabled"] = True
                    logger.info(f"Enabled caching for deterministic step: {step.id}")
        
        return workflow
    
    def _optimize_timeouts(self, workflow: WorkflowDefinition) -> WorkflowDefinition:
        """Optimize step timeouts based on step type."""
        
        for step in workflow.steps:
            if step.type == StepType.LLM_CALL:
                # LLM calls typically need more time
                if step.timeout_seconds < 60:
                    step.timeout_seconds = 60
                    logger.info(f"Increased timeout for LLM step: {step.id}")
            elif step.type == StepType.TRANSFORM:
                # Transform steps are usually fast
                if step.timeout_seconds > 30:
                    step.timeout_seconds = 30
                    logger.info(f"Optimized timeout for transform step: {step.id}")
        
        return workflow