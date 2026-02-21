import hashlib
import mimetypes
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.config import settings
from app.core.object_storage import (
    ObjectStorageError,
    build_knowledge_object_key,
    get_object_storage_client,
    make_object_uri,
    parse_object_uri,
)
from app.models.user import User
from app.models.agent import AgentModel
from app.models.knowledge import KnowledgeFile, KnowledgeChunk, KnowledgeFileStatus, FileType, KnowledgeSearch
from app.schemas.knowledge import (
    KnowledgeFileResponse, KnowledgeFileCreate, KnowledgeFileUpdate,
    KnowledgeChunkResponse, KnowledgeSearchResponse, KnowledgeSearchCreate,
    KnowledgeStats, FileUploadResponse, BatchUploadResponse, KnowledgeSearchResult
)
from app.api.auth import get_current_user

router = APIRouter()
object_storage_client = get_object_storage_client()


# Utility functions
def get_file_type(filename: str) -> FileType:
    """Determine file type from filename extension"""
    extension = filename.lower().split('.')[-1]
    
    if extension in ['txt', 'md', 'markdown']:
        return FileType.TEXT
    elif extension == 'pdf':
        return FileType.PDF
    elif extension in ['png', 'jpg', 'jpeg', 'gif', 'webp']:
        return FileType.IMAGE
    elif extension in ['mp4', 'avi', 'mov', 'mkv', 'webm']:
        return FileType.VIDEO
    elif extension in ['py', 'js', 'ts', 'java', 'cpp', 'c', 'php', 'rb', 'go']:
        return FileType.CODE
    elif extension in ['doc', 'docx']:
        return FileType.DOCUMENT
    else:
        return FileType.TEXT  # Default fallback


async def process_file_content(file_bytes: bytes, file_type: FileType) -> tuple[str, Optional[str]]:
    """Extract text content from uploaded file"""
    try:
        if file_type == FileType.TEXT:
            return file_bytes.decode('utf-8', errors='replace'), None
            
        elif file_type == FileType.PDF:
            # TODO: Implement PDF text extraction (using PyPDF2 or similar)
            return "", "PDF processing not yet implemented"
            
        elif file_type == FileType.IMAGE:
            # TODO: Implement OCR for images
            return "", "Image OCR processing not yet implemented"
            
        elif file_type == FileType.VIDEO:
            # TODO: Implement video transcription
            return "", "Video processing not yet implemented"
            
        elif file_type == FileType.CODE:
            return file_bytes.decode('utf-8', errors='replace'), None
            
        else:
            # For other file types, try to read as text
            try:
                return file_bytes.decode('utf-8', errors='replace'), None
            except:
                return "", "Unsupported file type for content extraction"
                
    except Exception as e:
        return "", f"Error processing file: {str(e)}"


def chunk_text_content(content: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """Split text content into overlapping chunks"""
    if not content:
        return []
    
    chunks = []
    start = 0
    content_length = len(content)
    
    while start < content_length:
        end = min(start + chunk_size, content_length)
        chunk = content[start:end]
        chunks.append(chunk)
        start = end - overlap if end < content_length else end
    
    return chunks


def calculate_content_hash(content: str) -> str:
    """Calculate SHA256 hash of content for deduplication"""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


# Knowledge File Management Endpoints
@router.get("/agents/{agent_id}/files", response_model=List[KnowledgeFileResponse])
async def get_knowledge_files(
    agent_id: int,
    skip: int = 0,
    limit: int = 100,
    status: Optional[KnowledgeFileStatus] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get knowledge files for an agent"""
    
    # Verify agent ownership
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Build query
    query = select(KnowledgeFile).where(KnowledgeFile.agent_id == agent_id)
    
    if status:
        query = query.where(KnowledgeFile.processing_status == status)
    
    query = query.offset(skip).limit(limit).order_by(KnowledgeFile.created_at.desc())
    
    result = await db.execute(query)
    files = result.scalars().all()
    
    return files


@router.post("/agents/{agent_id}/files", response_model=FileUploadResponse)
async def upload_knowledge_file(
    agent_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload a knowledge file for an agent"""
    
    # Verify agent ownership
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    content = await file.read()
    file_size = len(content)

    if file_size > settings.UPLOAD_MAX_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {settings.UPLOAD_MAX_SIZE} bytes"
        )
    
    # Determine file type
    file_type = get_file_type(file.filename)
    
    # Generate unique filename
    timestamp = int(__import__('time').time())
    file_hash = hashlib.md5(f"{file.filename}{timestamp}".encode()).hexdigest()[:8]
    stored_filename = f"{file_hash}_{file.filename}"

    try:
        # Create knowledge file record
        knowledge_file = KnowledgeFile(
            original_filename=file.filename,
            stored_filename=stored_filename,
            file_path="pending",
            file_type=file_type,
            file_size=file_size,
            mime_type=file.content_type,
            processing_status=KnowledgeFileStatus.PROCESSING,
            agent_id=agent_id
        )

        db.add(knowledge_file)
        await db.flush()

        object_key = build_knowledge_object_key(
            agent_id=agent_id,
            knowledge_file_id=knowledge_file.id,
            sha256=hashlib.sha256(content).hexdigest(),
            filename=file.filename,
        )
        content_type = file.content_type or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"
        try:
            stored_object = await object_storage_client.put_object_bytes(
                key=object_key,
                data=content,
                content_type=content_type,
                metadata={
                    "agent_id": str(agent_id),
                    "knowledge_file_id": str(knowledge_file.id),
                },
            )
        except ObjectStorageError as exc:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Object storage unavailable: {exc}",
            ) from exc

        knowledge_file.file_path = make_object_uri(stored_object.bucket, stored_object.key)
        knowledge_file.object_key = stored_object.key
        knowledge_file.object_size = stored_object.size
        knowledge_file.object_content_type = stored_object.content_type
        knowledge_file.object_etag = stored_object.etag
        knowledge_file.storage_provider = stored_object.provider
        knowledge_file.storage_bucket = stored_object.bucket

        # Process file content asynchronously (in a real app, use background tasks)
        content_text, error = await process_file_content(content, file_type)

        if error:
            knowledge_file.processing_status = KnowledgeFileStatus.FAILED
            knowledge_file.processing_error = error
        else:
            knowledge_file.content_text = content_text
            knowledge_file.processing_status = KnowledgeFileStatus.READY

            # Create chunks
            chunks = chunk_text_content(content_text)
            for i, chunk in enumerate(chunks):
                chunk_hash = calculate_content_hash(chunk)
                knowledge_chunk = KnowledgeChunk(
                    chunk_index=i,
                    content=chunk,
                    content_hash=chunk_hash,
                    knowledge_file_id=knowledge_file.id
                )
                db.add(knowledge_chunk)

        await db.commit()
        await db.refresh(knowledge_file)

        return FileUploadResponse(
            success=True,
            file_id=knowledge_file.id,
            filename=file.filename,
            message="File uploaded successfully",
            processing_status=knowledge_file.processing_status
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )


@router.delete("/agents/{agent_id}/files/{file_id}")
async def delete_knowledge_file(
    agent_id: int,
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a knowledge file"""
    
    # Verify agent ownership and file exists
    result = await db.execute(
        select(KnowledgeFile).where(
            and_(
                KnowledgeFile.id == file_id,
                KnowledgeFile.agent_id == agent_id,
                KnowledgeFile.agent.has(AgentModel.owner_id == current_user.id)
            )
        )
    )
    knowledge_file = result.scalar_one_or_none()
    
    if not knowledge_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge file not found"
        )
    
    # Delete object-backed file first, then fall back to legacy local files.
    object_deleted = False
    if knowledge_file.object_key:
        try:
            await object_storage_client.delete_object(knowledge_file.object_key)
            object_deleted = True
        except ObjectStorageError:
            object_deleted = False
    elif parse_object_uri(knowledge_file.file_path):
        _, key = parse_object_uri(knowledge_file.file_path) or ("", "")
        if key:
            try:
                await object_storage_client.delete_object(key)
                object_deleted = True
            except ObjectStorageError:
                object_deleted = False

    if not object_deleted and knowledge_file.file_path:
        from pathlib import Path

        legacy_path = Path(knowledge_file.file_path)
        if legacy_path.exists():
            try:
                legacy_path.unlink()
            except OSError:
                pass
    
    # Delete database record (cascade will delete chunks)
    await db.delete(knowledge_file)
    await db.commit()
    
    return {"message": "Knowledge file deleted successfully"}


@router.put("/agents/{agent_id}/files/{file_id}", response_model=KnowledgeFileResponse)
async def update_knowledge_file(
    agent_id: int,
    file_id: int,
    file_update: KnowledgeFileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update knowledge file metadata"""
    
    # Verify agent ownership and file exists
    result = await db.execute(
        select(KnowledgeFile).where(
            and_(
                KnowledgeFile.id == file_id,
                KnowledgeFile.agent_id == agent_id,
                KnowledgeFile.agent.has(AgentModel.owner_id == current_user.id)
            )
        )
    )
    knowledge_file = result.scalar_one_or_none()
    
    if not knowledge_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge file not found"
        )
    
    # Update fields
    update_data = file_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(knowledge_file, field, value)
    
    await db.commit()
    await db.refresh(knowledge_file)
    
    return knowledge_file


# Search Endpoints
@router.post("/search", response_model=KnowledgeSearchResponse)
async def search_knowledge(
    search_data: KnowledgeSearchCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search through agent's knowledge base"""
    
    start_time = import_time = __import__('time').time()
    
    # If agent_id specified, verify ownership
    if search_data.agent_id:
        result = await db.execute(
            select(AgentModel).where(
                and_(
                    AgentModel.id == search_data.agent_id,
                    AgentModel.owner_id == current_user.id
                )
            )
        )
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )
    
    # Simple text search implementation (can be enhanced with embeddings)
    query = select(KnowledgeChunk).options(
        selectinload(KnowledgeChunk.knowledge_file)
    )
    
    if search_data.agent_id:
        query = query.join(KnowledgeFile).where(KnowledgeFile.agent_id == search_data.agent_id)
    
    # Basic keyword matching
    if search_data.query:
        query = query.where(KnowledgeChunk.content.contains(search_data.query))
    
    query = query.limit(10).order_by(KnowledgeChunk.created_at.desc())
    
    result = await db.execute(query)
    chunks = result.scalars().all()
    
    # Convert to search results
    search_results = []
    for chunk in chunks:
        # Simple relevance score based on content length and match
        relevance_score = min(len(chunk.content) / 1000, 1.0)
        
        search_results.append(KnowledgeSearchResult(
            chunk_id=chunk.id,
            file_id=chunk.knowledge_file.id,
            file_name=chunk.knowledge_file.original_filename,
            content=chunk.content[:500] + "..." if len(chunk.content) > 500 else chunk.content,
            relevance_score=relevance_score,
            metadata=chunk.chunk_metadata
        ))
    
    response_time = __import__('time').time() - start_time
    
    # Log search for analytics
    search_record = KnowledgeSearch(
        query=search_data.query,
        search_type=search_data.search_type,
        results_count=len(search_results),
        response_time=response_time,
        top_results=[result.dict() for result in search_results[:5]],
        user_id=current_user.id,
        agent_id=search_data.agent_id
    )
    
    db.add(search_record)
    await db.commit()
    
    return KnowledgeSearchResponse(
        query=search_data.query,
        search_type=search_data.search_type,
        results=search_results,
        total_results=len(search_results),
        response_time=response_time,
        search_id=search_record.id
    )


@router.get("/agents/{agent_id}/stats", response_model=KnowledgeStats)
async def get_knowledge_stats(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get knowledge base statistics for an agent"""
    
    # Verify agent ownership
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Get file statistics
    files_result = await db.execute(
        select(KnowledgeFile).where(KnowledgeFile.agent_id == agent_id)
    )
    files = files_result.scalars().all()
    
    # Get chunk statistics
    chunks_result = await db.execute(
        select(KnowledgeChunk)
        .join(KnowledgeFile)
        .where(KnowledgeFile.agent_id == agent_id)
    )
    chunks = chunks_result.scalars().all()
    
    # Calculate statistics
    total_files = len(files)
    total_chunks = len(chunks)
    total_size = sum(f.file_size for f in files)
    
    # Files by type
    files_by_type = {}
    for file in files:
        file_type = file.file_type.value
        files_by_type[file_type] = files_by_type.get(file_type, 0) + 1
    
    # Processing status counts
    status_counts = {}
    for file in files:
        status = file.processing_status.value
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Recent searches
    recent_searches_result = await db.execute(
        select(KnowledgeSearch)
        .where(KnowledgeSearch.agent_id == agent_id)
        .order_by(KnowledgeSearch.created_at.desc())
        .limit(5)
    )
    recent_searches = recent_searches_result.scalars().all()
    
    return KnowledgeStats(
        total_files=total_files,
        total_chunks=total_chunks,
        total_size_bytes=total_size,
        files_by_type=files_by_type,
        processing_status_counts=status_counts,
        recent_searches=[
            {
                "query": search.query,
                "search_type": search.search_type,
                "results_count": search.results_count,
                "created_at": search.created_at.isoformat()
            }
            for search in recent_searches
        ]
    )
