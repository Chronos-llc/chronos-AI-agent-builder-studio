/**
 * Meta-Agent FUZZY API Service
 * 
 * Provides API methods for meta-agent command execution, session management,
 * and command history tracking.
 */
import axios from 'axios';
import type {
    CommandExecutionRequest,
    CommandExecutionResponse,
    CommandListResponse,
    MetaAgentSession,
    MetaAgentSessionCreate,
    MetaAgentCommand,
    SessionHistoryResponse,
    CommandFilters,
    MetaAgent,
    MetaAgentCreate,
    MetaAgentUpdate
} from '../types/metaAgent';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_ENDPOINT = '/api/meta-agent';

// Create axios instance with default config
const apiClient = axios.create({
    baseURL: `${API_BASE_URL}${API_ENDPOINT}`,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor for adding auth token if needed
apiClient.interceptors.request.use(
    (config) => {
        // Add auth token from localStorage if available
        const token = localStorage.getItem('auth_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        const message = error.response?.data?.detail || error.message || 'An error occurred';
        console.error('API Error:', message);
        return Promise.reject(error);
    }
);

// ============== Command Execution Methods ==============

/**
 * Execute a meta-agent command
 * @param command - Natural language command to execute
 * @param parameters - Optional parameters for the command
 * @param sessionId - Optional session ID for continuing a conversation
 */
export const executeCommand = async (
    command: string,
    parameters?: Record<string, unknown>,
    sessionId?: string
): Promise<CommandExecutionResponse> => {
    const request: CommandExecutionRequest = {
        command,
        parameters,
        session_id: sessionId,
    };

    const response = await apiClient.post<CommandExecutionResponse>('/execute', request);
    return response.data;
};

// ============== Command Management Methods ==============

/**
 * List commands with optional filtering
 * @param filters - Filter criteria for commands
 */
export const listCommands = async (
    filters?: CommandFilters
): Promise<CommandListResponse> => {
    const params = new URLSearchParams();
    
    if (filters?.session_id) {
        params.append('session_id', filters.session_id);
    }
    if (filters?.status) {
        params.append('status', filters.status);
    }
    if (filters?.limit) {
        params.append('limit', filters.limit.toString());
    }
    if (filters?.offset) {
        params.append('offset', filters.offset.toString());
    }

    const response = await apiClient.get<CommandListResponse>('/commands', { params });
    return response.data;
};

/**
 * Get a specific command by ID
 * @param commandId - The command ID
 */
export const getCommand = async (commandId: number): Promise<MetaAgentCommand> => {
    const response = await apiClient.get<MetaAgentCommand>(`/commands/${commandId}`);
    return response.data;
};

/**
 * Create a new command record
 * @param commandData - Command creation data
 */
export const createCommand = async (
    commandData: Omit<MetaAgentCommand, 'id' | 'created_at' | 'status'>
): Promise<MetaAgentCommand> => {
    const response = await apiClient.post<MetaAgentCommand>('/commands', commandData);
    return response.data;
};

// ============== Session Management Methods ==============

/**
 * Get session details including context and status
 * @param sessionId - The session ID
 */
export const getSession = async (sessionId: string): Promise<MetaAgentSession> => {
    const response = await apiClient.get<MetaAgentSession>(`/sessions/${sessionId}`);
    return response.data;
};

/**
 * Create a new session
 * @param metaAgentId - The meta-agent ID to use for the session
 */
export const createSession = async (
    metaAgentId: number
): Promise<MetaAgentSession> => {
    const sessionData: MetaAgentSessionCreate = { meta_agent_id: metaAgentId };
    const response = await apiClient.post<MetaAgentSession>('/sessions', sessionData);
    return response.data;
};

/**
 * Mark a session as completed
 * @param sessionId - The session ID to complete
 */
export const completeSession = async (sessionId: string): Promise<void> => {
    await apiClient.put(`/sessions/${sessionId}/complete`);
};

/**
 * Get command history for a session
 * @param sessionId - The session ID
 */
export const getSessionHistory = async (
    sessionId: string
): Promise<SessionHistoryResponse> => {
    const response = await apiClient.get<SessionHistoryResponse>(
        `/sessions/${sessionId}/history`
    );
    return response.data;
};

// ============== Meta-Agent CRUD Methods ==============

/**
 * Get all meta-agents
 * @param skip - Number of records to skip
 * @param limit - Maximum number of records to return
 * @param isActive - Filter by active status
 */
export const getMetaAgents = async (
    skip?: number,
    limit?: number,
    isActive?: boolean
): Promise<MetaAgent[]> => {
    const params: Record<string, unknown> = {};
    
    if (skip !== undefined) params.skip = skip;
    if (limit !== undefined) params.limit = limit;
    if (isActive !== undefined) params.is_active = isActive;

    const response = await apiClient.get<MetaAgent[]>('/', { params });
    return response.data;
};

/**
 * Get a specific meta-agent by ID
 * @param metaAgentId - The meta-agent ID
 */
export const getMetaAgent = async (metaAgentId: number): Promise<MetaAgent> => {
    const response = await apiClient.get<MetaAgent>(`/${metaAgentId}`);
    return response.data;
};

/**
 * Create a new meta-agent
 * @param metaAgentData - Meta-agent creation data
 */
export const createMetaAgent = async (
    metaAgentData: MetaAgentCreate
): Promise<MetaAgent> => {
    const response = await apiClient.post<MetaAgent>('/', metaAgentData);
    return response.data;
};

/**
 * Update a meta-agent
 * @param metaAgentId - The meta-agent ID
 * @param updateData - Update data
 */
export const updateMetaAgent = async (
    metaAgentId: number,
    updateData: MetaAgentUpdate
): Promise<MetaAgent> => {
    const response = await apiClient.put<MetaAgent>(`/${metaAgentId}`, updateData);
    return response.data;
};

/**
 * Delete a meta-agent
 * @param metaAgentId - The meta-agent ID
 */
export const deleteMetaAgent = async (metaAgentId: number): Promise<void> => {
    await apiClient.delete(`/${metaAgentId}`);
};

// ============== Default Export ==============

const metaAgentService = {
    // Command execution
    executeCommand,
    
    // Command management
    listCommands,
    getCommand,
    createCommand,
    
    // Session management
    getSession,
    createSession,
    completeSession,
    getSessionHistory,
    
    // Meta-agent CRUD
    getMetaAgents,
    getMetaAgent,
    createMetaAgent,
    updateMetaAgent,
    deleteMetaAgent,
};

export default metaAgentService;
