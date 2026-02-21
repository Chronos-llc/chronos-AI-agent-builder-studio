from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class VirtualComputerProvider(str, Enum):
    E2B = "e2b"


class VirtualComputerConfigBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    enabled: bool = Field(default=False)
    provider: VirtualComputerProvider = Field(default=VirtualComputerProvider.E2B)
    idle_timeout_seconds: int = Field(default=300, ge=30, le=3600)
    max_runtime_seconds: int = Field(default=900, ge=60, le=7200)
    memory_mb: int = Field(default=512, ge=128, le=8192)
    cpu_cores: float = Field(default=1.0, ge=0.25, le=8.0)
    allow_network: bool = Field(default=True)
    mcp_enabled: bool = Field(default=True)
    mcp_server_ids: Optional[List[str]] = Field(default=None)


class VirtualComputerConfigCreate(VirtualComputerConfigBase):
    pass


class VirtualComputerConfigUpdate(BaseModel):
    enabled: Optional[bool] = None
    provider: Optional[VirtualComputerProvider] = None
    idle_timeout_seconds: Optional[int] = Field(default=None, ge=30, le=3600)
    max_runtime_seconds: Optional[int] = Field(default=None, ge=60, le=7200)
    memory_mb: Optional[int] = Field(default=None, ge=128, le=8192)
    cpu_cores: Optional[float] = Field(default=None, ge=0.25, le=8.0)
    allow_network: Optional[bool] = None
    mcp_enabled: Optional[bool] = None
    mcp_server_ids: Optional[List[str]] = None


class VirtualComputerConfigResponse(VirtualComputerConfigBase):
    id: int
    agent_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VirtualComputerSessionResponse(BaseModel):
    session_id: str
    agent_id: int
    user_id: int
    created_at: datetime
    expires_at: datetime
    tools: Dict[str, Any]


class VirtualComputerExecuteRequest(BaseModel):
    code: str
    inputs: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    conversation_id: Optional[int] = None


class VirtualComputerExecuteResponse(BaseModel):
    session_id: str
    stdout: str
    stderr: str
    exit_code: Optional[int] = None
    duration_ms: int


class VirtualComputerMcpProxyRequest(BaseModel):
    operation_type: str
    payload: Dict[str, Any]
    server_id: Optional[str] = None
    group_name: Optional[str] = None
