export type LogLevel = 'info' | 'warning' | 'warn' | 'error' | 'debug';
export type LogSource = 'system' | 'action' | 'hook' | 'agent' | 'user' | string;

export interface LogEntry {
  id: string;
  timestamp: string;
  level: LogLevel;
  message: string;
  source: LogSource;
  context?: Record<string, unknown>;
  agentId?: string;
  actionId?: string;
  hookId?: string;
}

export interface LogFilter {
  levels?: ('info' | 'warning' | 'error' | 'debug')[];
  sources?: string[];
  startDate?: string;
  endDate?: string;
  searchTerm?: string;
  agentIds?: string[];
}

export interface LoggingState {
  logs: LogEntry[];
  filters: LogFilter;
  isLoading: boolean;
  error: string | null;
  autoScroll: boolean;
  realtime: boolean;
}

export interface LogExportOptions {
  format: 'json' | 'csv' | 'text';
  includeContext: boolean;
  startDate?: string;
  endDate?: string;
}

export interface PerformanceMetrics {
  executionTime: number;
  memoryUsage: number;
  cpuUsage: number;
  timestamp: string;
  actionId?: string;
  agentId?: string;
}

export interface DebugSession {
  id: string;
  agentId: string;
  startedAt: string;
  endedAt?: string;
  status: 'active' | 'completed' | 'failed';
  logs: LogEntry[];
  metrics: PerformanceMetrics[];
}

export interface LogAnalysisResult {
  errorCount: number;
  warningCount: number;
  infoCount: number;
  debugCount: number;
  mostCommonErrors: Array<{ message: string; count: number }>;
  performanceTrends: {
    avgExecutionTime: number;
    maxMemoryUsage: number;
  };
}

export type LogExportFormat = 'json' | 'csv' | 'text';
