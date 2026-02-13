"""
Workflow Generation API Endpoints

Provides API endpoints for workflow generation, template management,
execution tracking, and pattern recognition.
"""
import time
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.enhanced_mcp_manager import enhanced_mcp_manager
from app.core.virtual_computer import get_virtual_computer_manager
from app.core.workflow_generation_engine import WorkflowGenerationEngine
from app.models.user import User
from app.models.agent import AgentModel
from app.models.integration import Integration as IntegrationModel, IntegrationStatus, IntegrationVisibility
from app.models.usage import UserPlan, has_team_visibility_access
from app.models.workflow_generation import (
    WorkflowGenerationTemplate, GeneratedWorkflow, WorkflowGenerationExecution,
    WorkflowPattern, WorkflowStatus, ExecutionStatus, WorkflowCategory
)
from app.api.auth import get_current_user
from app.schemas.workflow_generation import (
    WorkflowTemplateCreate, WorkflowTemplateUpdate, WorkflowTemplateResponse,
    WorkflowTemplateListResponse,
    GeneratedWorkflowCreate, GeneratedWorkflowResponse, GeneratedWorkflowListResponse,
    WorkflowExecutionCreate, WorkflowExecutionResponse,
    WorkflowPatternResponse, WorkflowPatternListResponse,
    WorkflowGenerationRequest, WorkflowGenerationResponse,
    WorkflowExecutionRequest, WorkflowSchemaExecutionRequest,
    PatternRecognitionRequest, PatternRecognitionResponse,
    WorkflowOptimizationRequest, WorkflowOptimizationResponse
)

router = APIRouter()


# Initialize the workflow generation engine
workflow_engine = WorkflowGenerationEngine()


# ============== Workflow Generation Endpoints ==============

@router.post("/generate", response_model=WorkflowGenerationResponse)
async def generate_workflow(
    request: WorkflowGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a workflow from natural language description.
    
    Parses the description, matches against templates, and generates
    a workflow schema using AI-powered workflow generation.
    """
    start_time = time.time()
    
    try:
        # Generate workflow using the engine
        generated_workflow = await workflow_engine.generate_workflow(
            description=request.description,
            parameters=request.parameters,
            user_id=current_user.id
        )
        
        # Add to database
        generated_workflow.user_id = current_user.id
        db.add(generated_workflow)
        await db.commit()
        await db.refresh(generated_workflow)
        
        # Match template if available
        matched_template = None
        if request.parameters:
            matched_template = await workflow_engine.match_template(request.description)
        
        # Recognize patterns in the generated workflow
        pattern_matches = []
        pattern = await workflow_engine.recognize_pattern(generated_workflow.workflow_schema)
        if pattern:
            pattern_matches.append(pattern)
        
        # Get optimization suggestions
        optimized_schema = await workflow_engine.optimize_workflow(generated_workflow.workflow_schema)
        improvements = optimized_schema.get("_optimizations", {}).get("improvements", [])
        
        execution_time = (time.time() - start_time) * 1000
        
        return WorkflowGenerationResponse(
            workflow=generated_workflow,
            matched_template=matched_template,
            pattern_matches=pattern_matches,
            optimization_suggestions=improvements
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow generation failed: {str(e)}"
        )


# ============== Workflow Template Endpoints ==============

@router.get("/templates", response_model=WorkflowTemplateListResponse)
async def list_templates(
    category: Optional[WorkflowCategory] = None,
    is_public: Optional[bool] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List available workflow templates with optional filtering."""
    query = select(WorkflowGenerationTemplate)
    
    # Apply filters
    if category is not None:
        query = query.where(WorkflowGenerationTemplate.category == category)
    
    if is_public is not None:
        query = query.where(WorkflowGenerationTemplate.is_public == is_public)
    
    # Include user's private templates or public templates
    query = query.where(
        (WorkflowGenerationTemplate.is_public == True) |
        (WorkflowGenerationTemplate.user_id == current_user.id)
    )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    query = query.offset(offset).limit(limit).order_by(WorkflowGenerationTemplate.created_at.desc())
    
    result = await db.execute(query)
    templates = result.scalars().all()
    
    return WorkflowTemplateListResponse(
        templates=templates,
        total=total,
        limit=limit,
        offset=offset
    )


@router.post("/templates", response_model=WorkflowTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: WorkflowTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new workflow template."""
    template = WorkflowGenerationTemplate(
        name=template_data.name,
        description=template_data.description,
        category=template_data.category,
        template_schema=template_data.template_schema,
        parameters=template_data.parameters,
        is_public=template_data.is_public,
        user_id=current_user.id
    )
    
    db.add(template)
    await db.commit()
    await db.refresh(template)
    
    return template


@router.get("/templates/{template_id}", response_model=WorkflowTemplateResponse)
async def get_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific template by ID."""
    result = await db.execute(
        select(WorkflowGenerationTemplate).where(
            and_(
                WorkflowGenerationTemplate.id == template_id,
                (WorkflowGenerationTemplate.is_public == True) |
                (WorkflowGenerationTemplate.user_id == current_user.id)
            )
        )
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    return template


@router.put("/templates/{template_id}", response_model=WorkflowTemplateResponse)
async def update_template(
    template_id: int,
    template_update: WorkflowTemplateUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a workflow template."""
    result = await db.execute(
        select(WorkflowGenerationTemplate).where(
            and_(
                WorkflowGenerationTemplate.id == template_id,
                WorkflowGenerationTemplate.user_id == current_user.id
            )
        )
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found or you don't have permission to update it"
        )
    
    # Update fields
    update_data = template_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(template, field, value)
    
    await db.commit()
    await db.refresh(template)
    
    return template


@router.delete("/templates/{template_id}")
async def delete_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a workflow template."""
    result = await db.execute(
        select(WorkflowGenerationTemplate).where(
            and_(
                WorkflowGenerationTemplate.id == template_id,
                WorkflowGenerationTemplate.user_id == current_user.id
            )
        )
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found or you don't have permission to delete it"
        )
    
    await db.delete(template)
    await db.commit()
    
    return {"message": "Template deleted successfully"}


# ============== Generated Workflow Endpoints ==============

@router.get("/generated", response_model=GeneratedWorkflowListResponse)
async def list_generated_workflows(
    status: Optional[WorkflowStatus] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List generated workflows for the current user."""
    query = select(GeneratedWorkflow).where(
        GeneratedWorkflow.user_id == current_user.id
    )
    
    if status is not None:
        query = query.where(GeneratedWorkflow.status == status)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    query = query.offset(offset).limit(limit).order_by(GeneratedWorkflow.created_at.desc())
    
    result = await db.execute(query)
    workflows = result.scalars().all()
    
    return GeneratedWorkflowListResponse(
        workflows=workflows,
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/generated/{workflow_id}", response_model=GeneratedWorkflowResponse)
async def get_generated_workflow(
    workflow_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific generated workflow by ID."""
    result = await db.execute(
        select(GeneratedWorkflow).where(
            and_(
                GeneratedWorkflow.id == workflow_id,
                GeneratedWorkflow.user_id == current_user.id
            )
        )
    )
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    return workflow


# ============== Workflow Execution Endpoints ==============

@router.post("/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(
    request: WorkflowExecutionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Execute a generated workflow.
    
    Creates an execution record and processes the workflow with the
    provided input data.
    """
    start_time = time.time()
    
    # Verify workflow exists and belongs to user
    result = await db.execute(
        select(GeneratedWorkflow).where(
            and_(
                GeneratedWorkflow.id == request.workflow_id,
                GeneratedWorkflow.user_id == current_user.id
            )
        )
    )
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    workflow_schema = workflow.workflow_schema
    agent: Optional[AgentModel] = None
    if _workflow_requires_code_execution(workflow_schema):
        if not request.agent_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="agent_id is required for code_execution steps"
            )
        agent = await _get_agent_or_404(request.agent_id, current_user, db)

    # Create execution record
    execution = WorkflowGenerationExecution(
        generated_workflow_id=request.workflow_id,
        status=ExecutionStatus.RUNNING,
        input_data=request.input_data
    )
    db.add(execution)
    await db.commit()
    await db.refresh(execution)
    
    try:
        # Execute the workflow (simplified - in production would execute actual steps)
        output_data = await _execute_workflow_steps(
            workflow_schema,
            request.input_data,
            agent=agent,
            current_user=current_user
        )
        
        execution.status = ExecutionStatus.COMPLETED
        execution.output_data = output_data
        execution.execution_time_ms = (time.time() - start_time) * 1000
        
        await db.commit()
        await db.refresh(execution)
        
        return execution
        
    except HTTPException:
        raise
    except Exception as e:
        execution.status = ExecutionStatus.FAILED
        execution.error_message = str(e)
        execution.execution_time_ms = (time.time() - start_time) * 1000
        await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow execution failed: {str(e)}"
        )


@router.post("/execute-schema", response_model=WorkflowExecutionResponse)
async def execute_workflow_schema(
    request: WorkflowSchemaExecutionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Execute an ad-hoc workflow schema without persisting a generated workflow."""
    start_time = time.time()

    agent = await _get_agent_or_404(request.agent_id, current_user, db)

    try:
        output_data = await _execute_workflow_steps(
            request.workflow_schema,
            request.input_data,
            agent=agent,
            current_user=current_user
        )

        return WorkflowExecutionResponse(
            id=0,
            generated_workflow_id=0,
            status=ExecutionStatus.COMPLETED,
            input_data=request.input_data,
            output_data=output_data,
            execution_time_ms=(time.time() - start_time) * 1000,
            error_message=None,
            created_at=datetime.utcnow()
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow execution failed: {str(e)}"
        )


async def _execute_workflow_steps(
    workflow_schema: dict,
    input_data: Optional[dict],
    agent: Optional[AgentModel],
    current_user: User
) -> dict:
    """Execute workflow steps (simplified implementation)."""
    steps = workflow_schema.get("steps", [])
    results = {}
    logs = {"steps": {}}
    
    for step in steps:
        step_name = step.get("name", "unknown")
        step_type = step.get("type", "action")
        
        # Simulate step execution
        step_input = {**(input_data or {}), **(step.get("inputs", {}))}
        
        # Different step types would have different logic
        if step_type == "extract":
            results[step_name] = {"extracted": True, "data": step_input}
        elif step_type == "transform":
            results[step_name] = {"transformed": True, "data": step_input}
        elif step_type == "load":
            results[step_name] = {"loaded": True, "data": step_input}
        elif step_type == "api_call":
            results[step_name] = {"api_called": True, "response": step_input}
        elif step_type == "code_execution":
            if not agent:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="agent_id is required for code_execution steps"
                )
            config = agent.virtual_computer_configuration
            if not config or not config.enabled:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Virtual computer is disabled for this agent"
                )
            code = (step.get("config") or {}).get("code")
            if not code:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing code for step {step_name}"
                )
            manager = get_virtual_computer_manager()
            try:
                exec_result = await manager.execute_python(
                    agent_id=agent.id,
                    user_id=current_user.id,
                    code=code,
                    inputs=step_input,
                    idle_timeout_seconds=config.idle_timeout_seconds,
                    max_runtime_seconds=config.max_runtime_seconds,
                    server_ids=config.mcp_server_ids,
                    mcp_enabled=config.mcp_enabled
                )
            except RuntimeError as exc:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(exc)
                )

            results[step_name] = {
                "executed": True,
                "stdout": exec_result.get("stdout", ""),
                "stderr": exec_result.get("stderr", ""),
                "exit_code": exec_result.get("exit_code"),
                "duration_ms": exec_result.get("duration_ms", 0)
            }
            logs["steps"][step_name] = {
                "type": "code_execution",
                "stdout": exec_result.get("stdout", ""),
                "stderr": exec_result.get("stderr", ""),
                "exit_code": exec_result.get("exit_code"),
                "duration_ms": exec_result.get("duration_ms", 0)
            }
        elif step_type in {"integration_api_call", "integration_mcp_call"}:
            config = step.get("config") or {}
            request_url = config.get("url")
            method = (config.get("method") or "GET").upper()
            headers = config.get("headers") or {}
            body = config.get("body")
            params = config.get("params") or {}

            if not request_url:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing config.url for step {step_name}",
                )
            request_start = time.time()
            response_payload = await enhanced_mcp_manager.make_api_request(
                method=method,
                url=request_url,
                headers=headers,
                body=body,
                params=params,
                server_id=config.get("server_id"),
            )
            duration_ms = int((time.time() - request_start) * 1000)
            results[step_name] = {
                "executed": True,
                "integration_id": config.get("integration_id"),
                "node_type": step_type,
                "response": response_payload,
                "duration_ms": duration_ms,
            }
            logs["steps"][step_name] = {
                "type": step_type,
                "stdout": "",
                "stderr": "",
                "exit_code": 0,
                "duration_ms": duration_ms,
                "response": response_payload,
            }
        else:
            results[step_name] = {"executed": True, "result": step_input}
    
    return {"steps": results, "success": True, "logs": logs}


def _workflow_requires_code_execution(workflow_schema: dict) -> bool:
    steps = workflow_schema.get("steps", [])
    return any(step.get("type") == "code_execution" for step in steps)


async def _get_agent_or_404(agent_id: int, current_user: User, db: AsyncSession) -> AgentModel:
    result = await db.execute(
        select(AgentModel).where(
            and_(
                AgentModel.id == agent_id,
                AgentModel.owner_id == current_user.id
            )
        )
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return agent


# ============== Workflow Pattern Endpoints ==============

@router.get("/patterns", response_model=WorkflowPatternListResponse)
async def list_patterns(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all recognized workflow patterns."""
    result = await db.execute(
        select(WorkflowPattern).order_by(WorkflowPattern.usage_count.desc())
    )
    patterns = result.scalars().all()
    
    return WorkflowPatternListResponse(patterns=patterns)


@router.post("/patterns/recognize", response_model=PatternRecognitionResponse)
async def recognize_pattern(
    request: PatternRecognitionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Recognize patterns in a workflow schema.
    
    Analyzes the provided schema and returns matching patterns
    from the pattern library.
    """
    pattern = await workflow_engine.recognize_pattern(request.workflow_schema)
    
    return PatternRecognitionResponse(
        matched_pattern=pattern,
        confidence=0.85 if pattern else 0.0,
        similar_patterns=[],
    )


# ============== Workflow Optimization Endpoints ==============

@router.post("/optimize", response_model=WorkflowOptimizationResponse)
async def optimize_workflow(
    request: WorkflowOptimizationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Optimize a workflow schema for better performance.
    
    Analyzes the workflow and applies optimizations such as
    removing redundant steps and improving execution order.
    """
    optimized_schema = await workflow_engine.optimize_workflow(request.workflow_schema)
    improvements = optimized_schema.get("_optimizations", {}).get("improvements", [])
    
    return WorkflowOptimizationResponse(
        optimized_schema=optimized_schema,
        improvements=improvements,
        estimated_performance_gain=0.15 if improvements else 0.0
    )
@router.get("/integration-nodes")
async def list_integration_nodes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List published integrations that can be used as workflow nodes."""
    user_plan = (await db.execute(select(UserPlan).where(UserPlan.user_id == current_user.id))).scalar_one_or_none()

    query = select(IntegrationModel).where(
        IntegrationModel.status.in_([IntegrationStatus.APPROVED.value, IntegrationStatus.PUBLISHED.value]),
        IntegrationModel.is_workflow_node_enabled == True
    )
    if has_team_visibility_access(user_plan.plan_type if user_plan else None):
        query = query.where(
            IntegrationModel.visibility.in_(
                [IntegrationVisibility.PUBLIC.value, IntegrationVisibility.TEAM.value]
            )
        )
    else:
        query = query.where(IntegrationModel.visibility == IntegrationVisibility.PUBLIC.value)

    integrations = (await db.execute(query.order_by(IntegrationModel.name.asc()))).scalars().all()
    nodes = []
    for integration in integrations:
        node_type = "integration_mcp_call" if integration.integration_type == "mcp_server" else "integration_api_call"
        nodes.append(
            {
                "node_type": node_type,
                "integration_id": integration.id,
                "name": integration.name,
                "description": integration.description,
                "category": integration.category,
                "icon": integration.icon or integration.app_icon_url,
                "config_schema": integration.config_schema or {},
                "credentials_schema": integration.credentials_schema or {},
            }
        )
    return {"nodes": nodes, "total": len(nodes)}
