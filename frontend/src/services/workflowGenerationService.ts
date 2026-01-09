/**
 * Workflow Generation Service
 * 
 * API service for the Automated Workflow Generation System.
 * Provides methods for workflow generation, template management,
 * execution tracking, and pattern recognition.
 */

import axios from 'axios';
import type {
  WorkflowTemplate,
  WorkflowTemplateCreate,
  WorkflowTemplateUpdate,
  WorkflowTemplateListResponse,
  GeneratedWorkflow,
  GeneratedWorkflowCreate,
  GeneratedWorkflowListResponse,
  WorkflowExecution,
  WorkflowExecutionRequest,
  WorkflowPattern,
  WorkflowPatternListResponse,
  WorkflowGenerationRequest,
  WorkflowGenerationResponse,
  WorkflowSchema,
  WorkflowOptimizationRequest,
  WorkflowOptimizationResponse,
} from '../types/workflowGeneration';

const API_BASE = '/api/workflow-generation';

export const workflowGenerationService = {
  /**
   * Generate a workflow from natural language description
   */
  async generateWorkflow(
    description: string,
    parameters?: Record<string, any>,
    category?: string
  ): Promise<WorkflowGenerationResponse> {
    const response = await axios.post<WorkflowGenerationResponse>(`${API_BASE}/generate`, {
      description,
      parameters,
      category,
    });
    return response.data;
  },

  /**
   * List available workflow templates
   */
  async listTemplates(
    category?: string,
    isPublic?: boolean,
    limit: number = 100,
    offset: number = 0
  ): Promise<WorkflowTemplateListResponse> {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (isPublic !== undefined) params.append('is_public', String(isPublic));
    params.append('limit', String(limit));
    params.append('offset', String(offset));

    const response = await axios.get<WorkflowTemplateListResponse>(
      `${API_BASE}/templates?${params.toString()}`
    );
    return response.data;
  },

  /**
   * Create a new workflow template
   */
  async createTemplate(template: WorkflowTemplateCreate): Promise<WorkflowTemplate> {
    const response = await axios.post<WorkflowTemplate>(`${API_BASE}/templates`, template);
    return response.data;
  },

  /**
   * Get a specific template by ID
   */
  async getTemplate(templateId: number): Promise<WorkflowTemplate> {
    const response = await axios.get<WorkflowTemplate>(`${API_BASE}/templates/${templateId}`);
    return response.data;
  },

  /**
   * Update a workflow template
   */
  async updateTemplate(
    templateId: number,
    updates: WorkflowTemplateUpdate
  ): Promise<WorkflowTemplate> {
    const response = await axios.put<WorkflowTemplate>(
      `${API_BASE}/templates/${templateId}`,
      updates
    );
    return response.data;
  },

  /**
   * Delete a workflow template
   */
  async deleteTemplate(templateId: number): Promise<void> {
    await axios.delete(`${API_BASE}/templates/${templateId}`);
  },

  /**
   * List generated workflows
   */
  async listGeneratedWorkflows(
    status?: string,
    limit: number = 100,
    offset: number = 0
  ): Promise<GeneratedWorkflowListResponse> {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    params.append('limit', String(limit));
    params.append('offset', String(offset));

    const response = await axios.get<GeneratedWorkflowListResponse>(
      `${API_BASE}/generated?${params.toString()}`
    );
    return response.data;
  },

  /**
   * Get a specific generated workflow by ID
   */
  async getGeneratedWorkflow(workflowId: number): Promise<GeneratedWorkflow> {
    const response = await axios.get<GeneratedWorkflow>(`${API_BASE}/generated/${workflowId}`);
    return response.data;
  },

  /**
   * Execute a generated workflow
   */
  async executeWorkflow(request: WorkflowExecutionRequest): Promise<WorkflowExecution> {
    const response = await axios.post<WorkflowExecution>(`${API_BASE}/execute`, request);
    return response.data;
  },

  /**
   * List all workflow patterns
   */
  async listPatterns(): Promise<WorkflowPatternListResponse> {
    const response = await axios.get<WorkflowPatternListResponse>(`${API_BASE}/patterns`);
    return response.data;
  },

  /**
   * Recognize patterns in a workflow schema
   */
  async recognizePattern(workflowSchema: WorkflowSchema): Promise<any> {
    const response = await axios.post(`${API_BASE}/patterns/recognize`, {
      workflow_schema: workflowSchema,
    });
    return response.data;
  },

  /**
   * Optimize a workflow schema
   */
  async optimizeWorkflow(
    workflowSchema: WorkflowSchema
  ): Promise<WorkflowOptimizationResponse> {
    const response = await axios.post<WorkflowOptimizationResponse>(
      `${API_BASE}/optimize`,
      { workflow_schema: workflowSchema }
    );
    return response.data;
  },

  /**
   * Update a generated workflow
   */
  async updateGeneratedWorkflow(
    workflowId: number,
    updates: Partial<GeneratedWorkflowCreate>
  ): Promise<GeneratedWorkflow> {
    const response = await axios.put<GeneratedWorkflow>(
      `${API_BASE}/generated/${workflowId}`,
      updates
    );
    return response.data;
  },

  /**
   * Get execution history for a workflow
   */
  async getExecutionHistory(workflowId: number): Promise<WorkflowExecution[]> {
    const response = await axios.get<WorkflowExecution[]>(
      `${API_BASE}/generated/${workflowId}/executions`
    );
    return response.data;
  },
};

export default workflowGenerationService;
