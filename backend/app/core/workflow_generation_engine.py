"""
Workflow Generation Engine

Core engine for AI-powered workflow generation, pattern recognition,
and workflow optimization.
"""
import re
import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.models.workflow_generation import (
    WorkflowGenerationTemplate, GeneratedWorkflow, WorkflowGenerationExecution,
    WorkflowPattern, WorkflowStatus, ExecutionStatus, WorkflowCategory
)


class WorkflowGenerationEngine:
    """
    Engine for generating, optimizing, and managing workflows.
    
    Provides methods for:
    - Generating workflows from natural language descriptions
    - Matching descriptions to existing templates
    - Recognizing workflow patterns
    - Optimizing generated workflows
    """
    
    # Common workflow patterns for recognition
    PATTERN_KEYWORDS = {
        "data_pipeline": ["extract", "transform", "load", "etl", "pipeline", "data flow"],
        "api_integration": ["api", "request", "endpoint", "http", "rest", "webhook"],
        "automation": ["automate", "schedule", "trigger", "cron", "periodic"],
        "notification": ["notify", "email", "alert", "message", "send"],
        "document_processing": ["parse", "extract", "convert", "pdf", "document"],
        "machine_learning": ["train", "model", "predict", "ml", "ai", "inference"],
        "code_execution": ["python", "script", "code", "sandbox", "execute code", "run code"],
    }
    
    # Template categories for matching
    CATEGORY_TRIGGERS = {
        WorkflowCategory.DATA_PROCESSING: ["data", "process", "transform", "clean", "filter"],
        WorkflowCategory.API_INTEGRATION: ["api", "integration", "connect", "sync"],
        WorkflowCategory.ETL: ["etl", "extract", "load", "warehouse"],
        WorkflowCategory.MACHINE_LEARNING: ["ml", "machine learning", "model", "train", "predict"],
        WorkflowCategory.DOCUMENT_PROCESSING: ["document", "pdf", "parse", "extract text"],
        WorkflowCategory.NOTIFICATION: ["notify", "alert", "email", "message"],
        WorkflowCategory.SCHEDULING: ["schedule", "cron", "periodic", " recurring"],
    }
    
    def __init__(self):
        """Initialize the workflow generation engine."""
        self._template_cache: Dict[int, WorkflowGenerationTemplate] = {}
        self._pattern_cache: Dict[int, WorkflowPattern] = {}
    
    async def generate_workflow(
        self,
        description: str,
        parameters: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None
    ) -> GeneratedWorkflow:
        """
        Generate a workflow from a natural language description.
        
        Args:
            description: Natural language description of the desired workflow
            parameters: Optional input parameters for customization
            user_id: ID of the user creating the workflow
            
        Returns:
            GeneratedWorkflow instance
        """
        # Parse the description
        parsed_description = self.parse_description(description)
        
        # Match to existing template if available
        matched_template = None
        if parsed_description.get("template_match"):
            matched_template = parsed_description["template_match"]
        
        # Generate workflow schema
        if matched_template:
            workflow_schema = self.generate_from_template(matched_template, parameters or {})
        else:
            workflow_schema = self._generate_from_description(description, parameters)
        
        # Create the generated workflow
        generated_workflow = GeneratedWorkflow(
            template_id=matched_template.id if matched_template else None,
            user_id=user_id or 0,
            name=parsed_description.get("name", f"Workflow {datetime.now().strftime('%Y%m%d%H%M%S')}"),
            description=description,
            workflow_schema=workflow_schema,
            generation_params={
                "description": description,
                "parameters": parameters,
                "parsed_description": parsed_description,
                "matched_template_id": matched_template.id if matched_template else None,
            },
            status=WorkflowStatus.DRAFT
        )
        
        return generated_workflow
    
    def parse_description(self, description: str) -> Dict[str, Any]:
        """
        Parse a natural language description into structured data.
        
        Args:
            description: Natural language description
            
        Returns:
            Dictionary containing parsed information
        """
        description_lower = description.lower()
        
        # Extract key elements
        result = {
            "original_description": description,
            "intent": self._classify_intent(description_lower),
            "category": self._detect_category(description_lower),
            "complexity": self._estimate_complexity(description),
            "entities": self._extract_entities(description_lower),
            "actions": self._extract_actions(description_lower),
        }
        
        # Try to extract a name
        name = self._extract_name(description)
        if name:
            result["name"] = name
        
        # Check for template matches
        result["template_match"] = None
        
        return result
    
    def _classify_intent(self, description: str) -> str:
        """Classify the intent of the workflow description."""
        for intent, keywords in self.PATTERN_KEYWORDS.items():
            if any(keyword in description for keyword in keywords):
                return intent
        return "general"
    
    def _detect_category(self, description: str) -> WorkflowCategory:
        """Detect the category of the workflow."""
        for category, triggers in self.CATEGORY_TRIGGERS.items():
            if any(trigger in description for trigger in triggers):
                return category
        return WorkflowCategory.CUSTOM
    
    def _estimate_complexity(self, description: str) -> str:
        """Estimate the complexity of the workflow."""
        word_count = len(description.split())
        
        if word_count < 20:
            return "simple"
        elif word_count < 50:
            return "moderate"
        else:
            return "complex"
    
    def _extract_entities(self, description: str) -> List[str]:
        """Extract key entities from the description."""
        entities = []
        
        # Common entity patterns
        patterns = [
            r"(?:api|endpoint|service)\s*[=:]\s*([^\s,]+)",
            r"(?:file|document|data)\s*[=:]\s*([^\s,]+)",
            r"(?:database|table|collection)\s*[=:]\s*([^\s,]+)",
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            entities.extend(matches)
        
        return list(set(entities))
    
    def _extract_actions(self, description: str) -> List[str]:
        """Extract action verbs from the description."""
        action_patterns = [
            r"(?:create|add|new)\s+(\w+)",
            r"(?:get|fetch|retrieve)\s+(\w+)",
            r"(?:update|modify|change)\s+(\w+)",
            r"(?:delete|remove)\s+(\w+)",
            r"(?:send|dispatch)\s+(\w+)",
            r"(?:process|transform)\s+(\w+)",
        ]
        
        actions = []
        for pattern in action_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            actions.extend(matches)
        
        return list(set(actions))
    
    def _extract_name(self, description: str) -> Optional[str]:
        """Extract a workflow name from the description."""
        # Look for "name:" or "workflow:" prefix
        name_patterns = [
            r"(?:name|workflow)\s*[=:]\s*([^\n,]+)",
            r"(?:create|build|make)\s+(?:a\s+)?(\w+(?:\s+\w+){0,3})",
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                if len(name) <= 100:
                    return name
        
        return None
    
    async def match_template(
        self,
        description: str
    ) -> Optional[WorkflowGenerationTemplate]:
        """
        Match a description to an existing workflow template.
        
        Args:
            description: Natural language description
            
        Returns:
            Matching WorkflowGenerationTemplate or None
        """
        # This would typically query the database
        # For now, return None (no match)
        return None
    
    async def generate_from_template(
        self,
        template: WorkflowGenerationTemplate,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a workflow from a template with provided parameters.
        
        Args:
            template: WorkflowGenerationTemplate to use
            parameters: Parameters to customize the template
            
        Returns:
            Generated workflow schema
        """
        template_schema = template.template_schema
        
        # Apply parameters to the template
        workflow_schema = self._apply_parameters(template_schema, parameters)
        
        return workflow_schema
    
    def _apply_parameters(
        self,
        schema: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply parameters to a workflow schema."""
        # Deep copy to avoid modifying the original
        result = json.loads(json.dumps(schema))
        
        # Replace parameter placeholders
        def replace_placeholders(obj: Any) -> Any:
            if isinstance(obj, str):
                for key, value in parameters.items():
                    placeholder = f"{{{{{key}}}}}"
                    if placeholder in obj:
                        obj = obj.replace(placeholder, str(value))
                return obj
            elif isinstance(obj, dict):
                return {k: replace_placeholders(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_placeholders(item) for item in obj]
            return obj
        
        return replace_placeholders(result)
    
    async def recognize_pattern(
        self,
        workflow_schema: Dict[str, Any]
    ) -> Optional[WorkflowPattern]:
        """
        Recognize patterns in a workflow schema.
        
        Args:
            workflow_schema: The workflow schema to analyze
            
        Returns:
            Matching WorkflowPattern or None
        """
        # Extract key characteristics
        schema_str = json.dumps(workflow_schema).lower()
        
        # Match against known patterns
        for pattern_type, keywords in self.PATTERN_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in schema_str)
            if score >= 2:  # Threshold for pattern match
                return WorkflowPattern(
                    name=pattern_type,
                    description=f"Detected {pattern_type} pattern",
                    pattern_schema={"type": pattern_type, "score": score},
                    usage_count=1,
                    success_rate=0.85
                )
        
        return None
    
    async def optimize_workflow(
        self,
        workflow_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize a generated workflow for better performance.
        
        Args:
            workflow_schema: The workflow schema to optimize
            
        Returns:
            Optimized workflow schema
        """
        optimized = json.loads(json.dumps(workflow_schema))
        improvements = []
        
        # Common optimizations
        if "steps" in optimized:
            # Remove redundant steps
            steps = optimized["steps"]
            unique_steps = []
            seen_names = set()
            
            for step in steps:
                if step.get("name") not in seen_names:
                    unique_steps.append(step)
                    seen_names.add(step.get("name"))
            
            if len(unique_steps) < len(steps):
                optimized["steps"] = unique_steps
                improvements.append("Removed duplicate steps")
            
            # Optimize step ordering (topological sort for dependencies)
            optimized["steps"] = self._optimize_step_ordering(optimized["steps"])
            improvements.append("Optimized step ordering")
        
        # Add optimization metadata
        if improvements:
            optimized["_optimizations"] = {
                "applied_at": datetime.now().isoformat(),
                "improvements": improvements,
            }
        
        return optimized
    
    def _optimize_step_ordering(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize step ordering based on dependencies."""
        if not steps:
            return steps
        
        # Simple reordering: put independent steps first
        steps_with_deps = {i: step for i, step in enumerate(steps)}
        dependency_graph = {}
        
        for i, step in enumerate(steps):
            deps = step.get("depends_on", [])
            dependency_graph[i] = deps
        
        # Sort by dependency count (fewer dependencies first)
        sorted_indices = sorted(
            range(len(steps)),
            key=lambda i: len(dependency_graph.get(i, []))
        )
        
        return [steps[i] for i in sorted_indices]
    
    def _generate_from_description(
        self,
        description: str,
        parameters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate a workflow schema from a description without using a template.
        
        Args:
            description: Natural language description
            parameters: Optional parameters
            
        Returns:
            Generated workflow schema
        """
        parsed = self.parse_description(description)
        
        # Generate a basic workflow structure based on intent
        workflow = {
            "name": parsed.get("name", "Generated Workflow"),
            "description": description,
            "category": parsed.get("category", "custom"),
            "complexity": parsed.get("complexity", "simple"),
            "steps": self._generate_steps_from_intent(
                parsed.get("intent", "general"),
                parsed.get("actions", []),
                parameters
            ),
            "triggers": self._generate_triggers_from_intent(
                parsed.get("intent", "general")
            ),
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "generator_version": "1.0.0",
            }
        }
        
        return workflow
    
    def _generate_steps_from_intent(
        self,
        intent: str,
        actions: List[str],
        parameters: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate workflow steps based on intent."""
        steps = []
        
        if intent == "data_pipeline":
            steps = [
                {"name": "extract", "type": "extract", "description": "Extract data from source"},
                {"name": "transform", "type": "transform", "description": "Transform data"},
                {"name": "load", "type": "load", "description": "Load data to destination"},
            ]
        elif intent == "api_integration":
            steps = [
                {"name": "authenticate", "type": "authentication", "description": "Authenticate with API"},
                {"name": "fetch_data", "type": "api_call", "description": "Fetch data from API"},
                {"name": "process_response", "type": "transform", "description": "Process API response"},
            ]
        elif intent == "automation":
            steps = [
                {"name": "trigger", "type": "trigger", "description": "Trigger automation"},
                {"name": "execute_actions", "type": "action", "description": "Execute automated actions"},
                {"name": "notify", "type": "notification", "description": "Send notification"},
            ]
        elif intent == "code_execution":
            steps = [
                {"name": "prepare_code", "type": "code_execution", "description": "Execute Python code in sandbox"},
            ]
        else:
            # Generic workflow
            steps = [
                {"name": "start", "type": "start", "description": "Start workflow"},
            ]
            
            for action in actions[:3]:  # Limit to 3 actions
                steps.append({
                    "name": action.lower(),
                    "type": "action",
                    "description": f"Perform {action}",
                })
            
            steps.append({
                "name": "complete",
                "type": "end",
                "description": "Complete workflow",
            })
        
        # Add parameters as step inputs
        if parameters:
            for step in steps:
                step["inputs"] = parameters
        
        return steps
    
    def _generate_triggers_from_intent(self, intent: str) -> List[Dict[str, Any]]:
        """Generate triggers based on intent."""
        if intent == "automation":
            return [{"type": "schedule", "config": {"cron": "* * * * *"}}]
        elif intent == "api_integration":
            return [{"type": "webhook", "config": {}}]
        else:
            return [{"type": "manual", "config": {}}]
