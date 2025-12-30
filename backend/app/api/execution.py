from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Dict, Any, List, Optional
import json
import uuid
import time
import asyncio
from datetime import datetime

from app.core.database import get_db
from app.models.user import User
from app.models.agent import AgentModel, Action
from app.models.usage import UsageRecord, UsageType
from app.api.auth import get_current_user
from app.schemas.action import ActionExecutionRequest, ActionExecutionResponse, ActionExecutionLog

router = APIRouter()


class ExecutionEnvironment:
    """Sandboxed execution environment for actions"""
    
    def __init__(self, action_id: int, agent_id: int, user_id: int):
        self.action_id = action_id
        self.agent_id = agent_id
        self.user_id = user_id
        self.execution_id = str(uuid.uuid4())
        self.start_time = time.time()
        self.timeout = 30  # Default timeout in seconds
        self.max_memory = 100  # MB
        self.max_cpu = 0.8  # 80% CPU usage limit
        self.status = "initializing"
        self.logs = []
        self.metrics = {}
        self.result = None
        self.error = None
        
    async def initialize(self, db: AsyncSession):
        """Initialize execution environment"""
        self.status = "initialized"
        self.log("Execution environment initialized")
        
        # Load action configuration
        result = await db.execute(
            select(Action).where(Action.id == self.action_id)
        )
        action = result.scalar_one_or_none()
        
        if not action:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Action not found"
            )
        
        # Apply action-specific configuration
        self.timeout = action.timeout or self.timeout
        self.log(f"Timeout set to {self.timeout} seconds")
        
        return action
    
    def log(self, message: str, level: str = "info"):
        """Add log entry"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "message": message,
            "execution_id": self.execution_id
        }
        self.logs.append(log_entry)
        print(f"[{level.upper()}] {message}")
    
    def update_metrics(self, cpu_usage: float = None, memory_usage: float = None):
        """Update performance metrics"""
        if cpu_usage:
            self.metrics["cpu_usage"] = cpu_usage
        if memory_usage:
            self.metrics["memory_usage"] = memory_usage
        
        self.metrics["execution_time"] = time.time() - self.start_time
    
    async def validate_input(self, input_data: Dict[str, Any], action: Action):
        """Validate input against action schema"""
        self.log("Validating input data")
        
        # Check if input schema is defined
        if not action.input_schema:
            self.log("No input schema defined, skipping validation")
            return True
        
        try:
            # Basic validation - in production, use proper JSON schema validation
            required_fields = action.input_schema.get("required", [])
            
            for field in required_fields:
                if field not in input_data:
                    self.error = f"Missing required field: {field}"
                    self.log(f"Validation error: {self.error}", "error")
                    return False
            
            # Validate data types
            properties = action.input_schema.get("properties", {})
            for field, schema in properties.items():
                if field in input_data:
                    expected_type = schema.get("type")
                    actual_value = input_data[field]
                    
                    if expected_type == "string" and not isinstance(actual_value, str):
                        self.error = f"Field '{field}' should be string, got {type(actual_value).__name__}"
                        self.log(f"Validation error: {self.error}", "error")
                        return False
                    elif expected_type == "number" and not isinstance(actual_value, (int, float)):
                        self.error = f"Field '{field}' should be number, got {type(actual_value).__name__}"
                        self.log(f"Validation error: {self.error}", "error")
                        return False
                    elif expected_type == "boolean" and not isinstance(actual_value, bool):
                        self.error = f"Field '{field}' should be boolean, got {type(actual_value).__name__}"
                        self.log(f"Validation error: {self.error}", "error")
                        return False
            
            self.log("Input validation passed")
            return True
            
        except Exception as e:
            self.error = f"Validation error: {str(e)}"
            self.log(f"Validation error: {self.error}", "error")
            return False
    
    async def execute_action(self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None):
        """Execute the action in a sandboxed environment"""
        self.status = "executing"
        self.log("Starting action execution")
        
        # Simulate execution with timeout
        try:
            # In a real implementation, this would execute the actual code
            # For now, simulate different types of actions
            
            # Simulate execution time
            await asyncio.sleep(1)
            
            # Mock results based on action type
            if hasattr(self, 'action_type'):
                if self.action_type == "function":
                    self.result = {
                        "status": "success",
                        "output": f"Function executed with input: {input_data}",
                        "execution_time": time.time() - self.start_time
                    }
                elif self.action_type == "api_call":
                    self.result = {
                        "status": "success",
                        "response": {
                            "data": "API call successful",
                            "status": 200,
                            "input": input_data
                        }
                    }
                elif self.action_type == "web_scraping":
                    self.result = {
                        "status": "success",
                        "content": "Web scraping completed",
                        "url": input_data.get("url", "unknown"),
                        "elements_found": 15
                    }
                elif self.action_type == "code_execution":
                    self.result = {
                        "status": "success",
                        "output": "Code execution completed",
                        "return_value": "result_value",
                        "execution_time": time.time() - self.start_time
                    }
                else:
                    self.result = {
                        "status": "success",
                        "message": "Action executed successfully",
                        "input": input_data
                    }
            else:
                self.result = {
                    "status": "success",
                    "message": "Action executed successfully",
                    "input": input_data
                }
            
            self.log("Action execution completed successfully")
            self.status = "completed"
            
        except asyncio.TimeoutError:
            self.error = "Execution timed out"
            self.status = "timeout"
            self.log("Execution timed out", "error")
            
        except Exception as e:
            self.error = f"Execution error: {str(e)}"
            self.status = "error"
            self.log(f"Execution error: {self.error}", "error")
        
        finally:
            self.update_metrics()
    
    def validate_output(self, output_data: Dict[str, Any], action: Action):
        """Validate output against action schema"""
        self.log("Validating output data")
        
        if not action.output_schema:
            self.log("No output schema defined, skipping validation")
            return True
        
        try:
            # Basic output validation
            required_fields = action.output_schema.get("required", [])
            
            for field in required_fields:
                if field not in output_data:
                    self.error = f"Missing required output field: {field}"
                    self.log(f"Output validation error: {self.error}", "error")
                    return False
            
            self.log("Output validation passed")
            return True
            
        except Exception as e:
            self.error = f"Output validation error: {str(e)}"
            self.log(f"Output validation error: {self.error}", "error")
            return False
    
    def get_execution_response(self) -> ActionExecutionResponse:
        """Generate execution response"""
        duration_ms = int((time.time() - self.start_time) * 1000)
        
        return ActionExecutionResponse(
            execution_id=self.execution_id,
            status=self.status,
            result=self.result,
            error=self.error,
            logs=self.logs,
            timestamp=datetime.now(),
            metrics={
                "duration_ms": duration_ms,
                "memory_usage": self.metrics.get("memory_usage", 0),
                "cpu_usage": self.metrics.get("cpu_usage", 0),
                **self.metrics
            }
        )


@router.post("/actions/{action_id}/execute", response_model=ActionExecutionResponse)
async def execute_action(
    action_id: int,
    execution_request: ActionExecutionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Execute an action with validation and sandboxing"""
    
    # Verify action exists and belongs to user's agent
    result = await db.execute(
        select(Action).where(
            and_(
                Action.id == action_id,
                Action.agent.has(owner_id=current_user.id)
            )
        )
    )
    action = result.scalar_one_or_none()
    
    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found or not accessible"
        )
    
    # Create execution environment
    execution_env = ExecutionEnvironment(
        action_id=action_id,
        agent_id=action.agent_id,
        user_id=current_user.id
    )
    
    try:
        # Initialize environment
        action = await execution_env.initialize(db)
        execution_env.action_type = action.action_type
        
        # Validate input
        input_valid = await execution_env.validate_input(
            execution_request.input_data,
            action
        )
        
        if not input_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=execution_env.error or "Input validation failed"
            )
        
        # Execute action
        await execution_env.execute_action(
            execution_request.input_data,
            execution_request.context
        )
        
        # Validate output if execution was successful
        if execution_env.status == "completed" and execution_env.result:
            output_valid = execution_env.validate_output(
                execution_env.result,
                action
            )
            
            if not output_valid:
                execution_env.status = "error"
                execution_env.error = execution_env.error or "Output validation failed"
        
        # Create execution log
        execution_log = ActionExecutionLog(
            execution_id=execution_env.execution_id,
            action_id=action_id,
            status=execution_env.status,
            input_data=execution_request.input_data,
            output_data=execution_env.result,
            error=execution_env.error,
            duration_ms=int((time.time() - execution_env.start_time) * 1000),
            timestamp=datetime.now(),
            metrics=execution_env.metrics
        )
        
        # Store execution log (in a real implementation, this would be saved to database)
        # For now, just return the response
        
        # Track usage
        await track_usage(
            usage_data={
                "usage_type": UsageType.ACTION_EXECUTION,
                "amount": 1.0,
                "unit": "executions",
                "agent_id": action.agent_id,
                "action_id": action_id
            },
            current_user=current_user,
            db=db
        )
        
        return execution_env.get_execution_response()
        
    except Exception as e:
        error_response = ActionExecutionResponse(
            execution_id=execution_env.execution_id,
            status="error",
            result=None,
            error=f"Execution failed: {str(e)}",
            logs=execution_env.logs,
            timestamp=datetime.now(),
            metrics={
                "duration_ms": int((time.time() - execution_env.start_time) * 1000)
            }
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.error
        )


@router.get("/actions/{action_id}/history", response_model=List[ActionExecutionLog])
async def get_action_execution_history(
    action_id: int,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get execution history for an action"""
    
    # Verify action exists and belongs to user's agent
    result = await db.execute(
        select(Action).where(
            and_(
                Action.id == action_id,
                Action.agent.has(owner_id=current_user.id)
            )
        )
    )
    action = result.scalar_one_or_none()
    
    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found or not accessible"
        )
    
    # In a real implementation, this would query the execution logs database
    # For now, return mock data
    mock_history = []
    
    for i in range(min(limit, 5)):
        mock_history.append(ActionExecutionLog(
            execution_id=str(uuid.uuid4()),
            action_id=action_id,
            status="completed" if i % 2 == 0 else "error",
            input_data={"test": f"input_{i}"},
            output_data={"result": f"output_{i}"} if i % 2 == 0 else None,
            error="Mock error" if i % 2 != 0 else None,
            duration_ms=100 + i * 50,
            timestamp=datetime.now(),
            metrics={"cpu_usage": 0.3 + i * 0.05, "memory_usage": 50 + i * 10}
        ))
    
    return mock_history


@router.get("/actions/{action_id}/status")
async def get_action_status(
    action_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current status of an action"""
    
    # Verify action exists and belongs to user's agent
    result = await db.execute(
        select(Action).where(
            and_(
                Action.id == action_id,
                Action.agent.has(owner_id=current_user.id)
            )
        )
    )
    action = result.scalar_one_or_none()
    
    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found or not accessible"
        )
    
    return {
        "action_id": action_id,
        "status": action.status,
        "last_execution": datetime.now().isoformat(),
        "execution_count": 10 + action_id,  # Mock data
        "success_rate": 0.95,
        "average_execution_time": 150
    }


@router.post("/actions/{action_id}/validate")
async def validate_action(
    action_id: int,
    validation_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Validate action configuration and input"""
    
    # Verify action exists and belongs to user's agent
    result = await db.execute(
        select(Action).where(
            and_(
                Action.id == action_id,
                Action.agent.has(owner_id=current_user.id)
            )
        )
    )
    action = result.scalar_one_or_none()
    
    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found or not accessible"
        )
    
    # Create execution environment for validation
    execution_env = ExecutionEnvironment(
        action_id=action_id,
        agent_id=action.agent_id,
        user_id=current_user.id
    )
    
    try:
        # Initialize environment
        await execution_env.initialize(db)
        
        # Validate input
        input_valid = await execution_env.validate_input(
            validation_data.get("input_data", {}),
            action
        )
        
        # Validate configuration
        config_valid = True
        config_errors = []
        
        if not action.code:
            config_errors.append("Action code is required")
            config_valid = False
        
        if not action.action_type:
            config_errors.append("Action type is required")
            config_valid = False
        
        if action.timeout and action.timeout > 300:
            config_errors.append("Timeout exceeds maximum limit of 300 seconds")
            config_valid = False
        
        validation_result = {
            "action_id": action_id,
            "input_validation": {
                "valid": input_valid,
                "error": execution_env.error if not input_valid else None
            },
            "configuration_validation": {
                "valid": config_valid,
                "errors": config_errors if not config_valid else []
            },
            "overall_valid": input_valid and config_valid,
            "warnings": [],
            "recommendations": []
        }
        
        if action.timeout and action.timeout < 10:
            validation_result["warnings"].append("Short timeout may cause execution failures")
        
        if not action.retry_policy:
            validation_result["recommendations"].append("Consider adding a retry policy for resilience")
        
        return validation_result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )


async def track_usage(usage_data: Dict[str, Any], current_user: User, db: AsyncSession):
    """Track usage for action executions"""
    
    usage_record = UsageRecord(
        user_id=current_user.id,
        usage_type=usage_data["usage_type"],
        amount=usage_data["amount"],
        unit=usage_data["unit"],
        agent_id=usage_data.get("agent_id"),
        action_id=usage_data.get("action_id"),
        metadata={
            "execution_id": usage_data.get("execution_id"),
            "description": f"{usage_data['usage_type'].value} usage"
        }
    )
    
    db.add(usage_record)
    await db.commit()