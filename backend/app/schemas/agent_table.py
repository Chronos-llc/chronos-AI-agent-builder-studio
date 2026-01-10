from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


# Table Schema Definitions
class ColumnDefinition(BaseModel):
    """Definition of a table column"""
    name: str = Field(..., description="Column name")
    type: str = Field(..., description="Data type (string, integer, float, boolean, datetime, json)")
    required: bool = Field(default=False, description="Whether the column is required")
    unique: bool = Field(default=False, description="Whether values must be unique")
    default: Optional[Any] = Field(None, description="Default value for the column")
    description: Optional[str] = Field(None, description="Column description")


class TableSchema(BaseModel):
    """Schema definition for a table"""
    columns: List[ColumnDefinition] = Field(..., description="List of column definitions")
    
    @validator('columns')
    def validate_columns(cls, v):
        if not v:
            raise ValueError("At least one column is required")
        column_names = [col.name for col in v]
        if len(column_names) != len(set(column_names)):
            raise ValueError("Column names must be unique")
        return v


# Table CRUD Operations
class AgentTableCreate(BaseModel):
    """Schema for creating a new agent table"""
    name: str = Field(..., min_length=1, max_length=255, description="Table name (unique per agent)")
    display_name: str = Field(..., min_length=1, max_length=255, description="Human-readable name")
    description: Optional[str] = Field(None, description="Table description")
    schema: TableSchema = Field(..., description="Table schema definition")
    max_records: int = Field(default=10000, ge=1, le=100000, description="Maximum number of records")
    
    @validator('name')
    def validate_name(cls, v):
        # Ensure table name is valid (alphanumeric and underscores only)
        if not v.replace('_', '').isalnum():
            raise ValueError("Table name must contain only alphanumeric characters and underscores")
        return v.lower()


class AgentTableUpdate(BaseModel):
    """Schema for updating an agent table"""
    display_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    max_records: Optional[int] = Field(None, ge=1, le=100000)


class AgentTableResponse(BaseModel):
    """Response schema for agent table"""
    id: int
    agent_id: int
    user_id: int
    name: str
    display_name: str
    description: Optional[str]
    schema: Dict[str, Any]
    is_active: bool
    max_records: int
    record_count: int = Field(default=0, description="Current number of records")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Record CRUD Operations
class RecordCreate(BaseModel):
    """Schema for creating a new record"""
    data: Dict[str, Any] = Field(..., description="Record data matching table schema")
    record_key: Optional[str] = Field(None, max_length=255, description="Optional unique key")


class RecordUpdate(BaseModel):
    """Schema for updating a record"""
    data: Dict[str, Any] = Field(..., description="Updated record data")


class RecordResponse(BaseModel):
    """Response schema for a table record"""
    id: int
    table_id: int
    data: Dict[str, Any]
    record_key: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Query Operations
class QueryFilter(BaseModel):
    """Filter for querying records"""
    column: str = Field(..., description="Column name to filter on")
    operator: str = Field(..., description="Operator (eq, ne, gt, lt, gte, lte, contains, in)")
    value: Any = Field(..., description="Value to compare against")


class QueryRequest(BaseModel):
    """Schema for querying table records"""
    filters: Optional[List[QueryFilter]] = Field(None, description="List of filters to apply")
    sort_by: Optional[str] = Field(None, description="Column to sort by")
    sort_order: str = Field(default="asc", description="Sort order (asc or desc)")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum number of records to return")
    offset: int = Field(default=0, ge=0, description="Number of records to skip")


class QueryResponse(BaseModel):
    """Response schema for query results"""
    records: List[RecordResponse]
    total: int = Field(..., description="Total number of matching records")
    limit: int
    offset: int


# Bulk Operations
class BulkRecordCreate(BaseModel):
    """Schema for bulk record creation"""
    records: List[RecordCreate] = Field(..., max_items=1000, description="List of records to create")


class BulkRecordResponse(BaseModel):
    """Response schema for bulk operations"""
    created: int = Field(..., description="Number of records created")
    failed: int = Field(default=0, description="Number of records that failed")
    errors: Optional[List[str]] = Field(None, description="List of error messages")
