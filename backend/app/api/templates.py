from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Optional

from app.core.database import get_db
from app.models.user import User
from app.models.agent import AgentModel
from app.models.template import AgentTemplate, AgentTemplateCategory
from app.models.usage import UsageType
from app.api.auth import get_current_user
from app.schemas.template import (
    AgentTemplateCreate, AgentTemplateUpdate, AgentTemplateResponse,
    AgentTemplateCategoryCreate, AgentTemplateCategoryUpdate, AgentTemplateCategoryResponse,
    AgentFromTemplate
)
from app.schemas.agent import AgentCreate
from app.api.agents import create_agent

router = APIRouter()


@router.get("/", response_model=List[AgentTemplateResponse])
async def get_templates(
    category: Optional[str] = None,
    featured: Optional[bool] = None,
    public_only: bool = True,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get agent templates with optional filtering"""
    
    query = select(AgentTemplate)
    
    # Filter by category
    if category:
        query = query.where(AgentTemplate.category == category)
    
    # Filter by featured status
    if featured is not None:
        query = query.where(AgentTemplate.is_featured == featured)
    
    # Filter public templates only (unless user is authenticated and wants to see their own)
    if public_only:
        query = query.where(AgentTemplate.is_public == True)
    
    query = query.offset(skip).limit(limit).order_by(
        AgentTemplate.is_featured.desc(),
        AgentTemplate.usage_count.desc(),
        AgentTemplate.created_at.desc()
    )
    
    result = await db.execute(query)
    templates = result.scalars().all()
    
    return templates


@router.get("/{template_id}", response_model=AgentTemplateResponse)
async def get_template(
    template_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific template"""
    
    result = await db.execute(select(AgentTemplate).where(AgentTemplate.id == template_id))
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    return template


@router.post("/", response_model=AgentTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: AgentTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new agent template"""
    
    template = AgentTemplate(
        **template_data.dict(),
        created_by_user_id=current_user.id
    )
    
    db.add(template)
    await db.commit()
    await db.refresh(template)
    
    return template


@router.put("/{template_id}", response_model=AgentTemplateResponse)
async def update_template(
    template_id: int,
    template_update: AgentTemplateUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an agent template"""
    
    result = await db.execute(select(AgentTemplate).where(AgentTemplate.id == template_id))
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Check if user owns the template or is admin
    if template.created_by_user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this template"
        )
    
    # Update template
    update_data = template_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)
    
    await db.commit()
    await db.refresh(template)
    
    return template


@router.delete("/{template_id}")
async def delete_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an agent template"""
    
    result = await db.execute(select(AgentTemplate).where(AgentTemplate.id == template_id))
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Check if user owns the template or is admin
    if template.created_by_user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this template"
        )
    
    await db.delete(template)
    await db.commit()
    
    return {"message": "Template deleted successfully"}


@router.post("/{template_id}/create-agent", response_model=AgentTemplateResponse)
async def create_agent_from_template(
    template_id: int,
    agent_data: AgentFromTemplate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create an agent from a template"""
    
    # Get template
    result = await db.execute(select(AgentTemplate).where(AgentTemplate.id == template_id))
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Check if template is public or user owns it
    if not template.is_public and template.created_by_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Template is not public"
        )
    
    # Check user plan limits
    # This would typically check against user's current usage and plan limits
    
    # Create agent from template
    agent_create_data = AgentCreate(
        name=agent_data.agent_name,
        description=agent_data.agent_description or template.description,
        system_prompt=template.system_prompt,
        user_prompt_template=template.user_prompt_template,
        model_config=template.model_config,
        tags=template.tags
    )
    
    agent = await create_agent(
        agent_data=agent_create_data,
        current_user=current_user,
        db=db
    )
    
    # Increment template usage count
    template.usage_count += 1
    await db.commit()
    
    # Track usage for agent creation
    from app.api.usage import track_usage
    await track_usage(
        usage_data={
            "usage_type": UsageType.AGENT_CREATION,
            "amount": 1.0,
            "unit": "agents",
            "agent_id": agent.id
        },
        current_user=current_user,
        db=db
    )
    
    return template


@router.get("/categories/", response_model=List[AgentTemplateCategoryResponse])
async def get_template_categories(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Get template categories"""
    
    query = select(AgentTemplateCategory)
    
    if active_only:
        query = query.where(AgentTemplateCategory.is_active == True)
    
    query = query.order_by(AgentTemplateCategory.name)
    
    result = await db.execute(query)
    categories = result.scalars().all()
    
    return categories


@router.post("/categories/", response_model=AgentTemplateCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_template_category(
    category_data: AgentTemplateCategoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new template category (admin only)"""
    
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create categories"
        )
    
    category = AgentTemplateCategory(**category_data.dict())
    
    db.add(category)
    await db.commit()
    await db.refresh(category)
    
    return category


@router.get("/featured/", response_model=List[AgentTemplateResponse])
async def get_featured_templates(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get featured templates"""
    
    result = await db.execute(
        select(AgentTemplate)
        .where(AgentTemplate.is_featured == True, AgentTemplate.is_public == True)
        .order_by(AgentTemplate.usage_count.desc())
        .limit(limit)
    )
    
    templates = result.scalars().all()
    
    return templates