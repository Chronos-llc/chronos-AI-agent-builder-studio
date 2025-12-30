from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class KnowledgeFileStatus(str, Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"
    DELETED = "deleted"


class FileType(str, Enum):
    TEXT = "text"
    PDF = "pdf"
    IMAGE = "image"
    VIDEO = "video"
    CODE = "code"
    DOCUMENT = "document"


class KnowledgeFileBase(BaseModel):
    original_filename: str
    file_type: FileType
    file_size: int
    mime_type: Optional[str] = None
    content_summary: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class KnowledgeFileCreate(KnowledgeFileBase):
    pass


class KnowledgeFileUpdate(BaseModel):
    content_summary: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class KnowledgeFileResponse(KnowledgeFileBase):
    id: int
    stored_filename: str
    file_path: str
    content_text: Optional[str] = None
    content_keywords: Optional[List[str]] = None
    processing_status: KnowledgeFileStatus
    processing_error: Optional[str] = None
    agent_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class KnowledgeChunkBase(BaseModel):
    chunk_index: int
    content: str
    content_hash: str
    chunk_metadata: Optional[Dict[str, Any]] = None


class KnowledgeChunkCreate(KnowledgeChunkBase):
    knowledge_file_id: int


class KnowledgeChunkResponse(KnowledgeChunkBase):
    id: int
    knowledge_file_id: int
    embedding_vector: Optional[List[float]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class KnowledgeSearchBase(BaseModel):
    query: str
    search_type: str = "hybrid"  # "semantic", "keyword", "hybrid"
    agent_id: Optional[int] = None


class KnowledgeSearchCreate(KnowledgeSearchBase):
    pass


class KnowledgeSearchResponse(KnowledgeSearchBase):
    id: int
    results_count: int
    response_time: Optional[float] = None
    top_results: Optional[List[Dict[str, Any]]] = None
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class KnowledgeSearchResult(BaseModel):
    chunk_id: int
    file_id: int
    file_name: str
    content: str
    relevance_score: float
    metadata: Optional[Dict[str, Any]] = None


class KnowledgeSearchResponse(BaseModel):
    query: str
    search_type: str
    results: List[KnowledgeSearchResult]
    total_results: int
    response_time: float
    search_id: int


class FileUploadResponse(BaseModel):
    success: bool
    file_id: Optional[int] = None
    filename: str
    message: str
    processing_status: Optional[KnowledgeFileStatus] = None


class KnowledgeStats(BaseModel):
    total_files: int
    total_chunks: int
    total_size_bytes: int
    files_by_type: Dict[str, int]
    processing_status_counts: Dict[str, int]
    recent_searches: List[Dict[str, Any]]


class BatchUploadResponse(BaseModel):
    success: bool
    uploaded_files: List[FileUploadResponse]
    failed_files: List[FileUploadResponse]
    total_processed: int
    total_successful: int
    total_failed: int