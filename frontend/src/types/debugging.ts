export interface LogEntry {
  id: string;
  timestamp: string;
  level: 'debug' | 'info' | 'warning' | 'error' | 'critical';
  message: string;
  session_id: string;
  agent_id: number;
  user_id: number;
  context?: Record<string, any>;
  details?: Record<string, any>;
}

export interface DebugEvent {
  type: string;
  timestamp: string;
  session_id: string;
  agent_id: number;
  data?: Record<string, any>;
  event_type?: string;
  severity?: string;
  message?: string;
}

export interface ExecutionTrace {
  trace_id: string;
  session_id: string;
  agent_id: number;
  start_time: string;
  end_time?: string;
  status: string;
  steps?: Record<string, any>[];
  error?: string;
  timestamp?: string;
  function_name?: string;
  duration_ms?: number;
}

export interface BreakpointHit {
  id?: string;
  agent_id?: number;
  session_id?: string;
  location?: string;
  condition?: string;
  hit_count?: number;
  enabled?: boolean;
  created_at?: string;
  file?: string;
  line?: number;
  function_name?: string;
  variables?: Record<string, any>;
  status?: string;
}

export interface WatchExpressionResult {
  id?: string;
  agent_id?: number;
  session_id?: string;
  expression: string;
  name?: string;
  current_value?: string;
  created_at?: string;
  value?: string;
  type?: string;
  timestamp?: string;
}

export interface DebugSession {
  session_id: string;
  agent_id: number;
  user_id: number;
  start_time: string;
  status: string;
  debug_mode: boolean;
}

export interface DebugCommand {
  agent_id: number;
  command: string;
  parameters?: Record<string, any>;
}

export interface DebugResponse {
  success: boolean;
  message: string;
  data?: Record<string, any>;
}

export interface PerformanceMetrics {
  session_id: string;
  agent_id: number;
  uptime_seconds: number;
  execution_count: number;
  average_execution_time: number;
  error_rate: number;
  memory_usage: number;
  cpu_usage: number;
  active_breakpoints: number;
  watch_expressions: number;
  log_count: number;
  debug_mode: boolean;
}

export interface Breakpoint {
  id: string;
  agent_id: number;
  session_id: string;
  location: string;
  condition?: string;
  hit_count: number;
  enabled: boolean;
  created_at: string;
}

export interface WatchExpression {
  id: string;
  agent_id: number;
  session_id: string;
  expression: string;
  name: string;
  current_value?: string;
  created_at: string;
}

export interface DebugConfiguration {
  agent_id: number;
  auto_attach: boolean;
  break_on_errors: boolean;
  log_level: 'debug' | 'info' | 'warning' | 'error' | 'critical';
  max_log_entries: number;
  performance_monitoring: boolean;
  memory_profiling: boolean;
  cpu_profiling: boolean;
}

export interface LogFilter {
  level?: 'debug' | 'info' | 'warning' | 'error' | 'critical';
  start_time?: string;
  end_time?: string;
  search_text?: string;
  limit?: number;
}
