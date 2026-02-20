"""
Skills API Endpoints

Provides RESTful API for managing skills and skill installations.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, asc
from sqlalchemy.orm import joinedload
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import os
from pathlib import Path

from app.core.database import get_db
from app.models.user import User
from app.models.admin import AdminUser
from app.models.agent import AgentModel
from app.models.skills import Skill, AgentSkillInstallation
from app.api.auth import get_current_user
from app.schemas.skills import (
    SkillCreate, SkillUpdate, SkillResponse, SkillList,
    AgentSkillInstallationCreate, AgentSkillInstallationUpdate,
    AgentSkillInstallationResponse, AgentSkillInstallationList,
    SkillSearchParams, SkillExecutionRequest, SkillExecutionResponse,
    SkillStatistics
)
from app.core.skills_engine import skills_engine

router = APIRouter()
logger = logging.getLogger(__name__)


async def is_admin(user: User, db: AsyncSession) -> bool:
    """Check whether user has effective admin access."""
    if user.is_superuser:
        return True
    result = await db.execute(
        select(AdminUser).where(
            and_(
                AdminUser.user_id == user.id,
                AdminUser.is_active == True,
            )
        )
    )
    return result.scalar_one_or_none() is not None


# Skills Management Endpoints (Admin)
@router.get("/skills", response_model=SkillList)
async def get_skills(
    category: Optional[str] = Query(None, description="Filter by category"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_premium: Optional[bool] = Query(None, description="Filter by premium status"),
    search_query: Optional[str] = Query(None, description="Text search in name and description"),
    sort_by: str = Query("created_at", description="Sort field: created_at, install_count, name"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all skills with filtering and sorting"""
    
    # Base query
    query = select(Skill)
    
    # Apply filters
    if category:
        query = query.where(Skill.category == category)
    
    if tags:
        # Filter by tags (JSONB contains)
        for tag in tags:
            query = query.where(Skill.tags.contains([tag]))
    
    if is_active is not None:
        query = query.where(Skill.is_active == is_active)
    
    if is_premium is not None:
        query = query.where(Skill.is_premium == is_premium)
    
    if search_query:
        query = query.where(
            or_(
                Skill.name.ilike(f"%{search_query}%"),
                Skill.display_name.ilike(f"%{search_query}%"),
                Skill.description.ilike(f"%{search_query}%")
            )
        )
    
    # Sorting
    sort_field = Skill.created_at
    if sort_by == "install_count":
        sort_field = Skill.install_count
    elif sort_by == "name":
        sort_field = Skill.name
    
    if sort_order == "asc":
        query = query.order_by(asc(sort_field))
    else:
        query = query.order_by(desc(sort_field))
    
    # Count total
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar_one()
    
    # Pagination
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    skills = result.scalars().all()
    
    return {
        "items": [SkillResponse.from_orm(skill) for skill in skills],
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_more": page * page_size < total
    }


@router.get("/skills/{skill_id}", response_model=SkillResponse)
async def get_skill(
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific skill by ID"""
    
    result = await db.execute(select(Skill).where(Skill.id == skill_id))
    skill = result.scalar_one_or_none()
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    return SkillResponse.from_orm(skill)


@router.post("/skills", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
async def create_skill(
    skill_data: SkillCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new skill (admin only)"""
    
    if not await is_admin(current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Check if skill name already exists
    result = await db.execute(select(Skill).where(Skill.name == skill_data.name))
    existing_skill = result.scalar_one_or_none()
    
    if existing_skill:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skill with this name already exists"
        )
    
    # Validate skill file exists
    skill_path = skill_data.file_path
    if not os.path.isabs(skill_path):
        skill_path = os.path.join(os.getcwd(), skill_path)
    
    if not os.path.exists(skill_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Skill file not found: {skill_data.file_path}"
        )
    
    # Validate skill file
    validation_result = skills_engine.validate_skill_file(skill_path)
    if not validation_result['valid']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid skill file: {', '.join(validation_result['errors'])}"
        )
    
    # Get file size
    file_size = os.path.getsize(skill_path)
    
    # Create skill
    skill = Skill(
        name=skill_data.name,
        display_name=skill_data.display_name,
        description=skill_data.description,
        category=skill_data.category,
        icon=skill_data.icon,
        version=skill_data.version,
        parameters=skill_data.parameters,
        tags=skill_data.tags,
        file_path=skill_data.file_path,
        file_size=file_size,
        content_preview=skill_data.content_preview,
        is_active=skill_data.is_active,
        is_premium=skill_data.is_premium,
        created_by=current_user.id
    )
    
    db.add(skill)
    await db.commit()
    await db.refresh(skill)
    
    logger.info(f"Created skill: {skill.name} (ID: {skill.id})")
    
    return SkillResponse.from_orm(skill)


@router.put("/skills/{skill_id}", response_model=SkillResponse)
async def update_skill(
    skill_id: int,
    skill_update: SkillUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update skill (admin only)"""
    
    if not await is_admin(current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Get skill
    result = await db.execute(select(Skill).where(Skill.id == skill_id))
    skill = result.scalar_one_or_none()
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    # Update fields
    update_data = skill_update.dict(exclude_unset=True)
    
    # Validate file path if updated
    if "file_path" in update_data:
        skill_path = update_data["file_path"]
        if not os.path.isabs(skill_path):
            skill_path = os.path.join(os.getcwd(), skill_path)
        
        if not os.path.exists(skill_path):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Skill file not found: {update_data['file_path']}"
            )
        
        # Validate skill file
        validation_result = skills_engine.validate_skill_file(skill_path)
        if not validation_result['valid']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid skill file: {', '.join(validation_result['errors'])}"
            )
        
        # Update file size
        update_data['file_size'] = os.path.getsize(skill_path)
        
        # Reload skill in engine
        skills_engine.reload_skill(skill_path)
    
    # Apply updates
    for field, value in update_data.items():
        setattr(skill, field, value)
    
    await db.commit()
    await db.refresh(skill)
    
    logger.info(f"Updated skill: {skill.name} (ID: {skill.id})")
    
    return SkillResponse.from_orm(skill)


@router.delete("/skills/{skill_id}")
async def delete_skill(
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete skill (admin only)"""
    
    if not await is_admin(current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Get skill
    result = await db.execute(select(Skill).where(Skill.id == skill_id))
    skill = result.scalar_one_or_none()
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    # Delete skill (cascade will handle installations)
    await db.delete(skill)
    await db.commit()
    
    logger.info(f"Deleted skill: {skill.name} (ID: {skill.id})")
    
    return {"message": "Skill deleted successfully"}


@router.post("/skills/discover")
async def discover_skills(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Discover skills from file system and sync with database (admin only)"""
    
    if not await is_admin(current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        # Discover skills from file system
        discovered_skills = skills_engine.discover_skills()
        
        created_count = 0
        updated_count = 0
        errors = []
        
        for skill_info in discovered_skills:
            try:
                # Check if skill already exists
                result = await db.execute(select(Skill).where(Skill.name == skill_info['name']))
                existing_skill = result.scalar_one_or_none()
                
                if existing_skill:
                    # Update existing skill
                    for field, value in skill_info.items():
                        if field not in ['name']:  # Don't update name
                            setattr(existing_skill, field, value)
                    updated_count += 1
                else:
                    # Create new skill
                    skill = Skill(
                        **skill_info,
                        created_by=current_user.id
                    )
                    db.add(skill)
                    created_count += 1
                
            except Exception as e:
                errors.append(f"Error processing {skill_info['name']}: {str(e)}")
                logger.error(f"Error processing skill {skill_info['name']}: {str(e)}")
        
        await db.commit()
        
        return {
            "message": "Skills discovery completed",
            "discovered": len(discovered_skills),
            "created": created_count,
            "updated": updated_count,
            "errors": errors
        }
        
    except Exception as e:
        logger.error(f"Error discovering skills: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to discover skills: {str(e)}"
        )


@router.get("/categories/list")
@router.get("/skills/categories/list")
async def get_skill_categories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get list of all skill categories"""
    
    result = await db.execute(
        select(Skill.category, func.count(Skill.id).label('count'))
        .where(Skill.category.isnot(None))
        .group_by(Skill.category)
        .order_by(desc('count'))
    )
    
    categories = result.all()
    
    return {
        "categories": [
            {"name": cat.category, "count": cat.count}
            for cat in categories
        ]
    }


# Agent Skill Installation Endpoints (Users)
@router.get("/agents/{agent_id}/skills", response_model=AgentSkillInstallationList)
async def get_agent_skills(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all skills installed on an agent"""
    
    # Verify agent exists and belongs to user
    result = await db.execute(select(AgentModel).where(
        and_(
            AgentModel.id == agent_id,
            AgentModel.owner_id == current_user.id
        )
    ))
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or not owned by user"
        )
    
    # Get installations with skill details
    result = await db.execute(
        select(AgentSkillInstallation)
        .where(AgentSkillInstallation.agent_id == agent_id)
        .options(joinedload(AgentSkillInstallation.skill))
    )
    installations = result.scalars().all()
    
    # Convert to response format
    installation_responses = []
    for installation in installations:
        response = AgentSkillInstallationResponse.from_orm(installation)
        if installation.skill:
            response.skill = SkillResponse.from_orm(installation.skill)
        installation_responses.append(response)
    
    return {
        "items": installation_responses,
        "total": len(installation_responses)
    }


@router.post("/agents/{agent_id}/skills", response_model=AgentSkillInstallationResponse, status_code=status.HTTP_201_CREATED)
async def install_skill_to_agent(
    agent_id: int,
    installation_data: AgentSkillInstallationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Install a skill to an agent"""
    
    # Verify agent exists and belongs to user
    result = await db.execute(select(AgentModel).where(
        and_(
            AgentModel.id == agent_id,
            AgentModel.owner_id == current_user.id
        )
    ))
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or not owned by user"
        )
    
    # Verify skill exists and is active
    result = await db.execute(select(Skill).where(Skill.id == installation_data.skill_id))
    skill = result.scalar_one_or_none()
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    if not skill.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skill is not active"
        )
    
    # Check if already installed
    result = await db.execute(select(AgentSkillInstallation).where(
        and_(
            AgentSkillInstallation.agent_id == agent_id,
            AgentSkillInstallation.skill_id == installation_data.skill_id
        )
    ))
    existing_installation = result.scalar_one_or_none()
    
    if existing_installation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skill already installed on this agent"
        )
    
    # Create installation
    installation = AgentSkillInstallation(
        agent_id=agent_id,
        skill_id=installation_data.skill_id,
        configuration=installation_data.configuration
    )
    
    db.add(installation)
    
    # Increment skill install count
    skill.install_count += 1
    
    await db.commit()
    await db.refresh(installation)
    
    # Load skill details
    result = await db.execute(
        select(AgentSkillInstallation)
        .where(AgentSkillInstallation.id == installation.id)
        .options(joinedload(AgentSkillInstallation.skill))
    )
    installation = result.scalar_one()
    
    logger.info(f"Installed skill {skill.name} to agent {agent_id}")
    
    response = AgentSkillInstallationResponse.from_orm(installation)
    if installation.skill:
        response.skill = SkillResponse.from_orm(installation.skill)
    
    return response


@router.put("/agents/{agent_id}/skills/{installation_id}", response_model=AgentSkillInstallationResponse)
async def update_agent_skill_installation(
    agent_id: int,
    installation_id: int,
    installation_update: AgentSkillInstallationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update skill installation configuration"""
    
    # Verify agent exists and belongs to user
    result = await db.execute(select(AgentModel).where(
        and_(
            AgentModel.id == agent_id,
            AgentModel.owner_id == current_user.id
        )
    ))
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or not owned by user"
        )
    
    # Get installation
    result = await db.execute(
        select(AgentSkillInstallation)
        .where(
            and_(
                AgentSkillInstallation.id == installation_id,
                AgentSkillInstallation.agent_id == agent_id
            )
        )
        .options(joinedload(AgentSkillInstallation.skill))
    )
    installation = result.scalar_one_or_none()
    
    if not installation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill installation not found"
        )
    
    # Update fields
    update_data = installation_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(installation, field, value)
    
    await db.commit()
    await db.refresh(installation)
    
    response = AgentSkillInstallationResponse.from_orm(installation)
    if installation.skill:
        response.skill = SkillResponse.from_orm(installation.skill)
    
    return response


@router.delete("/agents/{agent_id}/skills/{installation_id}")
async def uninstall_skill_from_agent(
    agent_id: int,
    installation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Uninstall a skill from an agent"""
    
    # Verify agent exists and belongs to user
    result = await db.execute(select(AgentModel).where(
        and_(
            AgentModel.id == agent_id,
            AgentModel.owner_id == current_user.id
        )
    ))
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or not owned by user"
        )
    
    # Get installation
    result = await db.execute(
        select(AgentSkillInstallation)
        .where(
            and_(
                AgentSkillInstallation.id == installation_id,
                AgentSkillInstallation.agent_id == agent_id
            )
        )
        .options(joinedload(AgentSkillInstallation.skill))
    )
    installation = result.scalar_one_or_none()
    
    if not installation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill installation not found"
        )
    
    skill_id = installation.skill_id
    
    # Delete installation
    await db.delete(installation)
    
    # Decrement skill install count
    result = await db.execute(select(Skill).where(Skill.id == skill_id))
    skill = result.scalar_one_or_none()
    if skill and skill.install_count > 0:
        skill.install_count -= 1
    
    await db.commit()
    
    logger.info(f"Uninstalled skill from agent {agent_id}")
    
    return {"message": "Skill uninstalled successfully"}


# Skill Execution Endpoint
@router.post("/skills/{skill_id}/execute", response_model=SkillExecutionResponse)
async def execute_skill(
    skill_id: int,
    execution_request: SkillExecutionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Execute a skill with given parameters"""
    
    # Get skill
    result = await db.execute(select(Skill).where(Skill.id == skill_id))
    skill = result.scalar_one_or_none()
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    if not skill.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skill is not active"
        )
    
    try:
        # Execute skill using skills engine
        result = skills_engine.execute_skill(
            skill_path=skill.file_path,
            parameters=execution_request.parameters or {},
            context=execution_request.context or {}
        )
        
        return SkillExecutionResponse(**result)
        
    except Exception as e:
        logger.error(f"Error executing skill {skill_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute skill: {str(e)}"
        )


# Statistics Endpoint
@router.get("/statistics/overview", response_model=SkillStatistics)
@router.get("/skills/statistics/overview", response_model=SkillStatistics)
async def get_skills_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get skills system statistics"""
    
    # Total skills
    total_result = await db.execute(select(func.count(Skill.id)))
    total_skills = total_result.scalar_one()
    
    # Active skills
    active_result = await db.execute(select(func.count(Skill.id)).where(Skill.is_active == True))
    active_skills = active_result.scalar_one()
    
    # Total installations
    installations_result = await db.execute(select(func.count(AgentSkillInstallation.id)))
    total_installations = installations_result.scalar_one()
    
    # Popular categories
    categories_result = await db.execute(
        select(Skill.category, func.count(Skill.id).label('count'))
        .where(Skill.category.isnot(None))
        .group_by(Skill.category)
        .order_by(desc('count'))
        .limit(5)
    )
    categories = categories_result.all()
    popular_categories = [
        {"category": cat.category, "count": cat.count}
        for cat in categories
    ]
    
    # Recent skills
    recent_result = await db.execute(
        select(Skill)
        .where(Skill.is_active == True)
        .order_by(desc(Skill.created_at))
        .limit(5)
    )
    recent_skills = recent_result.scalars().all()
    
    return {
        "total_skills": total_skills,
        "active_skills": active_skills,
        "total_installations": total_installations,
        "popular_categories": popular_categories,
        "recent_skills": [SkillResponse.from_orm(skill) for skill in recent_skills]
    }
