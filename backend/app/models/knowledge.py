from sqlalchemy import Column, String, Text, Integer, Float, Boolean, ForeignKey, JSON, DateTime, Enum
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class KnowledgeFileStatus(enum.Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"
    DELETED = "deleted"


class FileType(enum.Enum):
    TEXT = "text"
    PDF = "pdf"
    IMAGE = "image"
    VIDEO = "video"
    CODE = "code"
    DOCUMENT = "document"


class KnowledgeFile(BaseModel):
    __tablename__ = "knowledge_files"
    
    # File information
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False, unique=True)
    file_path = Column(String(500), nullable=False)
    file_type = Column(Enum(FileType), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=True)
    
    # Content processing
    content_text = Column(Text, nullable=True)  # Extracted text content
    content_summary = Column(Text, nullable=True)  # AI-generated summary
    content_keywords = Column(JSON, nullable=True)  # Extracted keywords
    processing_status = Column(Enum(KnowledgeFileStatus), default=KnowledgeFileStatus.UPLOADING)
    processing_error = Column(Text, nullable=True)
    
    # Metadata
    additional_metadata = Column(JSON, nullable=True)  # Additional file metadata
    tags = Column(JSON, nullable=True)  # User-defined tags
    
    # Agent association
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    
    # Relationships
    agent = relationship("AgentModel", back_populates="knowledge_files")
    chunks = relationship("KnowledgeChunk", back_populates="knowledge_file", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<KnowledgeFile(id={self.id}, filename='{self.original_filename}', type='{self.file_type}')>"


class KnowledgeChunk(BaseModel):
    __tablename__ = "knowledge_chunks"
    
    # Chunk information
    chunk_index = Column(Integer, nullable=False)  # Order within the file
    content = Column(Text, nullable=False)  # Chunk content
    content_hash = Column(String(64), nullable=False)  # SHA256 hash for deduplication
    
    # Embeddings and search
    embedding_vector = Column(JSON, nullable=True)  # Vector embedding for semantic search
    chunk_metadata = Column(JSON, nullable=True)  # Metadata for this chunk
    
    # File association
    knowledge_file_id = Column(Integer, ForeignKey("knowledge_files.id"), nullable=False)
    
    # Relationships
    knowledge_file = relationship("KnowledgeFile", back_populates="chunks")
    
    def __repr__(self):
        return f"<KnowledgeChunk(id={self.id}, file_id={self.knowledge_file_id}, index={self.chunk_index})>"


class KnowledgeSearch(BaseModel):
    __tablename__ = "knowledge_searches"
    
    # Search information
    query = Column(Text, nullable=False)
    search_type = Column(String(20), nullable=False)  # "semantic", "keyword", "hybrid"
    results_count = Column(Integer, default=0)
    response_time = Column(Float, nullable=True)  # Search response time in seconds
    
    # Results (store top results for analytics)
    top_results = Column(JSON, nullable=True)  # Top search results
    
    # User and agent context
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="knowledge_searches")
    agent = relationship("AgentModel", back_populates="knowledge_searches")
    
    def __repr__(self):
        return f"<KnowledgeSearch(id={self.id}, query='{self.query[:50]}...', type='{self.search_type}')>"