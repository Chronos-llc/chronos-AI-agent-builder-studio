/**
 * Meta-Agent FUZZY TypeScript Types
 * 
 * Defines TypeScript interfaces matching backend schemas for the meta-agent API.
 */

// ============== Permission Levels ==============

export enum PermissionLevel {
    VIEWER = "viewer",
    EDITOR = "editor",
    ADMIN = "admin",
    SUPERUSER = "superuser"
}

// ============== Command Status ==============

export enum CommandStatus {
    PENDING = "pending",
    EXECUTING = "executing",
    COMPLETED = "completed",
    FAILED = "failed"
}

// ============== Session Status ==============

export enum SessionStatus {
    ACTIVE = "active",
    COMPLETED = "completed",
    TIMEOUT = "timeout"
}

// ============== MetaAgent Types ==============

export interface MetaAgent {
    id: number;
    name: string;
    description?: string;
    is_active: boolean;
    permission_level: PermissionLevel;
    allowed_actions?: string[];
    configuration?: Record<string, unknown>;
    created_at: string;
    updated_at: string;
}

export interface MetaAgentCreate {
    name: string;
    description?: string;
    is_active?: boolean;
    permission_level?: PermissionLevel;
    allowed_actions?: string[];
    configuration?: Record<string, unknown>;
}

export interface MetaAgentUpdate {
    name?: string;
    description?: string;
    is_active?: boolean;
    permission_level?: PermissionLevel;
    allowed_actions?: string[];
    configuration?: Record<string, unknown>;
}

// ============== MetaAgentCommand Types ==============

export interface MetaAgentCommand {
    id: number;
    meta_agent_id: number;
    session_id?: string;
    command_type: string;
    intent: string;
    parameters?: Record<string, unknown>;
    status: CommandStatus;
    result?: Record<string, unknown>;
    error_message?: string;
    execution_time_ms?: number;
    created_at: string;
}

export interface MetaAgentCommandCreate {
    meta_agent_id: number;
    session_id?: string;
    command_type: string;
    intent: string;
    parameters?: Record<string, unknown>;
}

// ============== MetaAgentSession Types ==============

export interface MetaAgentSession {
    id: string;
    user_id: number;
    meta_agent_id: number;
    status: SessionStatus;
    context?: SessionContext;
    created_at: string;
    updated_at: string;
    completed_at?: string;
}

export interface MetaAgentSessionCreate {
    meta_agent_id: number;
}

export interface SessionContext {
    history: CommandHistoryEntry[];
    metadata?: Record<string, unknown>;
}

export interface CommandHistoryEntry {
    command: string;
    intent: string;
    result: Record<string, unknown>;
    timestamp: string;
}

// ============== Command Execution Types ==============

export interface CommandExecutionRequest {
    command: string;
    parameters?: Record<string, unknown>;
    session_id?: string;
}

export interface CommandExecutionResponse {
    session_id: string;
    result: Record<string, unknown>;
    execution_time_ms: number;
    command_id?: number;
}

// ============== Command List Types ==============

export interface CommandListResponse {
    commands: MetaAgentCommand[];
    total: number;
    limit: number;
    offset: number;
}

// ============== Session History Response ==============

export interface SessionHistoryResponse {
    session: MetaAgentSession;
    history: MetaAgentCommand[];
    context: SessionContext;
}

// ============== Pagination Types ==============

export interface PaginationParams {
    limit?: number;
    offset?: number;
}

export interface CommandFilters extends PaginationParams {
    session_id?: string;
    status?: CommandStatus;
}

// ============== UI State Types ==============

export interface CommandExecutionState {
    isExecuting: boolean;
    currentCommand?: string;
    error?: string;
    executionTime?: number;
}

export interface SessionState {
    currentSession?: MetaAgentSession;
    isLoading: boolean;
    error?: string;
}

export interface CommandHistoryItem {
    id: number;
    command: string;
    intent: string;
    status: CommandStatus;
    executionTime: number;
    result?: Record<string, unknown>;
    error?: string;
    timestamp: string;
    expanded?: boolean;
}
