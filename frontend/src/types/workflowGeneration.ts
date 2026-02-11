/**
 * Workflow Generation Types
 * 
 * TypeScript interfaces matching the backend Pydantic schemas
 * for the Automated Workflow Generation System.
 */

// Enum Types
export type WorkflowStatus = 'draft' | 'active' | 'archived';
export type ExecutionStatus = 'pending' | 'running' | 'completed' | 'failed';
export type WorkflowCategory = 
  | 'data_processing' 
  | 'api_integration' 
  | 'automation' 
  | 'etl' 
  | 'machine_learning' 
  | 'document_processing' 
  | 'notification' 
  | 'scheduling' 
  | 'custom';

// Base Types
export interface WorkflowTemplateBase {
  name: string;
  description?: string;
  category: WorkflowCategory;
}

export interface GeneratedWorkflowBase {
  name: string;
  description?: string;
}

export interface WorkflowPatternBase {
  name: string;
  description?: string;
}

// Workflow Template
export interface WorkflowTemplate extends WorkflowTemplateBase {
  id: number;
  template_schema: WorkflowSchema;
  parameters?: Record<string, any>;
  is_public: boolean;
  user_id?: number;
  created_at: string;
  updated_at: string;
}

export interface WorkflowTemplateCreate extends WorkflowTemplateBase {
  template_schema: WorkflowSchema;
  parameters?: Record<string, any>;
  is_public?: boolean;
}

export interface WorkflowTemplateUpdate {
  name?: string;
  description?: string;
  category?: WorkflowCategory;
  template_schema?: WorkflowSchema;
  parameters?: Record<string, any>;
  is_public?: boolean;
}

export interface WorkflowTemplateListResponse {
  templates: WorkflowTemplate[];
  total: number;
  limit: number;
  offset: number;
}

// Generated Workflow
export interface GeneratedWorkflow extends GeneratedWorkflowBase {
  id: number;
  template_id?: number;
  user_id: number;
  workflow_schema: WorkflowSchema;
  generation_params?: Record<string, any>;
  status: WorkflowStatus;
  created_at: string;
  updated_at: string;
}

export interface GeneratedWorkflowCreate extends GeneratedWorkflowBase {
  template_id?: number;
  workflow_schema: WorkflowSchema;
  generation_params?: Record<string, any>;
  status?: WorkflowStatus;
}

export interface GeneratedWorkflowListResponse {
  workflows: GeneratedWorkflow[];
  total: number;
  limit: number;
  offset: number;
}

// Workflow Execution
export interface WorkflowExecution {
  id: number;
  generated_workflow_id: number;
  status: ExecutionStatus;
  input_data?: Record<string, any>;
  output_data?: Record<string, any>;
  execution_time_ms?: number;
  error_message?: string;
  created_at: string;
}

export interface WorkflowExecutionCreate {
  generated_workflow_id: number;
  input_data?: Record<string, any>;
}

export interface WorkflowExecutionRequest {
  workflow_id: number;
  agent_id: number;
  input_data?: Record<string, any>;
}

export interface WorkflowSchemaExecutionRequest {
  agent_id: number;
  workflow_schema: WorkflowSchema;
  input_data?: Record<string, any>;
}

// Workflow Pattern
export interface WorkflowPattern extends WorkflowPatternBase {
  id: number;
  pattern_schema: Record<string, any>;
  usage_count: number;
  success_rate: number;
  created_at: string;
  updated_at: string;
}

export interface WorkflowPatternListResponse {
  patterns: WorkflowPattern[];
}

// Workflow Schema
export interface WorkflowSchema {
  name: string;
  description?: string;
  category?: WorkflowCategory;
  complexity?: 'simple' | 'moderate' | 'complex';
  steps: WorkflowStep[];
  triggers?: WorkflowTrigger[];
  metadata?: Record<string, any>;
  _optimizations?: {
    applied_at?: string;
    improvements?: string[];
  };
}

export interface WorkflowStep {
  name: string;
  type: string;
  description?: string;
  inputs?: Record<string, any>;
  outputs?: Record<string, any>;
  depends_on?: string[];
  config?: Record<string, any>;
}

export interface WorkflowTrigger {
  type: 'manual' | 'schedule' | 'webhook' | 'event';
  config?: Record<string, any>;
}

// Generation Request/Response
export interface WorkflowGenerationRequest {
  description: string;
  parameters?: Record<string, any>;
  category?: WorkflowCategory;
}

export interface WorkflowGenerationResponse {
  workflow: GeneratedWorkflow;
  matched_template?: WorkflowTemplate;
  pattern_matches: WorkflowPattern[];
  optimization_suggestions: string[];
}

// Pattern Recognition
export interface PatternRecognitionRequest {
  workflow_schema: WorkflowSchema;
}

export interface PatternRecognitionResponse {
  matched_pattern?: WorkflowPattern;
  confidence: number;
  similar_patterns: WorkflowPattern[];
}

// Optimization
export interface WorkflowOptimizationRequest {
  workflow_schema: WorkflowSchema;
}

export interface WorkflowOptimizationResponse {
  optimized_schema: WorkflowSchema;
  improvements: string[];
  estimated_performance_gain: number;
}

// Workflow Builder State
export interface WorkflowBuilderState {
  currentSchema: WorkflowSchema | null;
  selectedStep: string | null;
  isDirty: boolean;
  isLoading: boolean;
  error: string | null;
}

// AI Generator State
export interface AIWorkflowGeneratorState {
  description: string;
  parameters: Record<string, any>;
  isGenerating: boolean;
  generatedWorkflow: GeneratedWorkflow | null;
  suggestions: string[];
  error: string | null;
}

// Pattern Visualizer State
export interface PatternVisualizerState {
  patterns: WorkflowPattern[];
  selectedPattern: WorkflowPattern | null;
  isLoading: boolean;
}
