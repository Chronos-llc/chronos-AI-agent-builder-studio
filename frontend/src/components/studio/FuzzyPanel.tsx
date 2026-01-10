/**
 * FuzzyPanel - Main Component for Meta-Agent FUZZY Interface
 * 
 * Provides command input, session display, command history,
 * real-time execution, and error handling.
 */
import React, { useState, useCallback, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import {
    Send,
    Loader2,
    RefreshCw,
    Terminal,
    Clock,
    CheckCircle,
    XCircle,
    AlertCircle,
    History,
    ChevronDown,
    ChevronUp,
    Play,
    Plus
} from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { ScrollArea } from '../ui/scroll-area';
import metaAgentService from '../../services/metaAgentService';
import type {
    CommandExecutionResponse,
    MetaAgentSession,
    CommandHistoryItem,
    SessionStatus,
    CommandStatus
} from '../../types/metaAgent';

// ============== Helper Components ==============

const StatusBadge: React.FC<{ status: CommandStatus | SessionStatus }> = ({ status }) => {
    const getStatusConfig = (status: CommandStatus | SessionStatus) => {
        switch (status) {
            case 'completed':
            case 'active':
                return { color: 'bg-green-100 text-green-800', icon: CheckCircle, label: status };
            case 'executing':
            case 'pending':
                return { color: 'bg-yellow-100 text-yellow-800', icon: Clock, label: status };
            case 'failed':
            case 'timeout':
                return { color: 'bg-red-100 text-red-800', icon: XCircle, label: status };
            default:
                return { color: 'bg-gray-100 text-gray-800', icon: AlertCircle, label: status };
        }
    };

    const config = getStatusConfig(status);
    const Icon = config.icon;

    return (
        <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
            <Icon className="w-3 h-3" />
            <span className="capitalize">{config.label}</span>
        </span>
    );
};

// ============== Main Component ==============

interface FuzzyPanelProps {
    agentId?: number;
}

export const FuzzyPanel: React.FC<FuzzyPanelProps> = ({ agentId = 1 }) => {
    const queryClient = useQueryClient();
    
    // State
    const [command, setCommand] = useState('');
    const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
    const [commandHistory, setCommandHistory] = useState<CommandHistoryItem[]>([]);
    const [expandedCommands, setExpandedCommands] = useState<Set<number>>(new Set());
    const [error, setError] = useState<string | null>(null);

    // Fetch current session
    const { 
        data: currentSession, 
        isLoading: isSessionLoading,
        refetch: refetchSession 
    } = useQuery({
        queryKey: ['meta-agent-session', currentSessionId],
        queryFn: () => currentSessionId ? metaAgentService.getSession(currentSessionId) : Promise.resolve(undefined),
        enabled: !!currentSessionId,
    });

    // Execute command mutation
    const executeCommandMutation = useMutation({
        mutationFn: (cmd: string) => metaAgentService.executeCommand(cmd, undefined, currentSessionId || undefined),
        onSuccess: (response: CommandExecutionResponse) => {
            // Update session ID if new
            if (!currentSessionId) {
                setCurrentSessionId(response.session_id);
            }

            // Add to command history
            const historyItem: CommandHistoryItem = {
                id: response.command_id || Date.now(),
                command: command,
                intent: response.result?.intent as string || 'unknown',
                status: 'completed',
                executionTime: response.execution_time_ms,
                result: response.result,
                timestamp: new Date().toISOString(),
            };
            
            setCommandHistory(prev => [historyItem, ...prev]);
            setCommand('');
            setError(null);
            toast.success('Command executed successfully');
            
            // Invalidate session query to refresh data
            queryClient.invalidateQueries({ queryKey: ['meta-agent-session', response.session_id] });
        },
        onError: (err: Error) => {
            const errorMessage = err.message || 'Failed to execute command';
            setError(errorMessage);
            toast.error(errorMessage);
            
            // Add failed command to history
            const historyItem: CommandHistoryItem = {
                id: Date.now(),
                command: command,
                intent: 'unknown',
                status: 'failed',
                executionTime: 0,
                error: errorMessage,
                timestamp: new Date().toISOString(),
            };
            
            setCommandHistory(prev => [historyItem, ...prev]);
        },
    });

    // Create new session mutation
    const createSessionMutation = useMutation({
        mutationFn: () => metaAgentService.createSession(agentId),
        onSuccess: (session: MetaAgentSession) => {
            setCurrentSessionId(session.id);
            toast.success('New session created');
            setCommandHistory([]);
            setError(null);
        },
        onError: (err: Error) => {
            toast.error('Failed to create session');
        },
    });

    // Complete session mutation
    const completeSessionMutation = useMutation({
        mutationFn: () => currentSessionId ? metaAgentService.completeSession(currentSessionId) : Promise.resolve(),
        onSuccess: () => {
            setCurrentSessionId(null);
            toast.success('Session completed');
            setCommandHistory([]);
        },
        onError: (err: Error) => {
            toast.error('Failed to complete session');
        },
    });

    // Fetch session history when session changes
    useEffect(() => {
        if (currentSessionId) {
            refetchSession();
        }
    }, [currentSessionId, refetchSession]);

    // Handle command submission
    const handleSubmit = useCallback((e: React.FormEvent) => {
        e.preventDefault();
        if (!command.trim() || executeCommandMutation.isPending) {
            return;
        }
        executeCommandMutation.mutate(command.trim());
    }, [command, executeCommandMutation]);

    // Handle new session creation
    const handleCreateSession = useCallback(() => {
        createSessionMutation.mutate();
    }, [createSessionMutation]);

    // Handle session completion
    const handleCompleteSession = useCallback(() => {
        if (currentSessionId) {
            completeSessionMutation.mutate();
        }
    }, [currentSessionId, completeSessionMutation]);

    // Toggle command expansion
    const toggleCommandExpansion = useCallback((commandId: number) => {
        setExpandedCommands(prev => {
            const newSet = new Set(prev);
            if (newSet.has(commandId)) {
                newSet.delete(commandId);
            } else {
                newSet.add(commandId);
            }
            return newSet;
        });
    }, []);

    // Get execution time display
    const formatExecutionTime = (ms: number): string => {
        if (ms < 1000) return `${ms.toFixed(0)}ms`;
        if (ms < 60000) return `${(ms / 1000).toFixed(2)}s`;
        return `${(ms / 60000).toFixed(2)}m`;
    };

    // Check if executing
    const isExecuting = executeCommandMutation.isPending;

    return (
        <div className="flex flex-col h-full bg-background text-foreground">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-border">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                        <Terminal className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                        <h2 className="font-semibold">Meta-Agent FUZZY</h2>
                        <p className="text-sm text-muted-foreground">
                            Natural language command execution
                        </p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    {currentSessionId ? (
                        <>
                            <Badge variant="outline" className="font-mono text-xs">
                                {currentSessionId.slice(0, 8)}...
                            </Badge>
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={handleCreateSession}
                                disabled={createSessionMutation.isPending}
                            >
                                <Plus className="w-4 h-4 mr-1" />
                                New Session
                            </Button>
                            <Button
                                variant="destructive"
                                size="sm"
                                onClick={handleCompleteSession}
                                disabled={completeSessionMutation.isPending}
                            >
                                Complete
                            </Button>
                        </>
                    ) : (
                        <Button
                            size="sm"
                            onClick={handleCreateSession}
                            disabled={createSessionMutation.isPending}
                        >
                            <Play className="w-4 h-4 mr-1" />
                            Start Session
                        </Button>
                    )}
                </div>
            </div>

            {/* Session Status */}
            {currentSession && (
                <div className="px-4 py-2 border-b border-border bg-muted/50">
                    <div className="flex items-center justify-between text-sm">
                        <div className="flex items-center gap-2">
                            <span className="text-muted-foreground">Session:</span>
                            <StatusBadge status={currentSession.status} />
                            <span className="text-muted-foreground">
                                Created: {new Date(currentSession.created_at).toLocaleString()}
                            </span>
                        </div>
                        <div className="flex items-center gap-4">
                            <span className="text-muted-foreground">
                                Commands: {commandHistory.length}
                            </span>
                            <span className="text-muted-foreground">
                                Context: {currentSession.context?.history?.length || 0} items
                            </span>
                        </div>
                    </div>
                </div>
            )}

            {/* Error Display */}
            {error && (
                <div className="mx-4 mt-4 p-3 rounded-md bg-destructive/10 border border-destructive/20 flex items-start gap-2">
                    <AlertCircle className="w-4 h-4 text-destructive mt-0.5" />
                    <div className="flex-1">
                        <p className="text-sm text-destructive font-medium">Execution Error</p>
                        <p className="text-sm text-destructive/80">{error}</p>
                    </div>
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setError(null)}
                        className="text-destructive hover:text-destructive"
                    >
                        Dismiss
                    </Button>
                </div>
            )}

            {/* Command Input */}
            <div className="p-4 border-b border-border">
                <form onSubmit={handleSubmit} className="flex gap-2">
                    <div className="relative flex-1">
                        <Input
                            type="text"
                            value={command}
                            onChange={(e) => setCommand(e.target.value)}
                            placeholder="Enter a natural language command..."
                            disabled={isExecuting}
                            className="pr-10"
                        />
                        {isExecuting && (
                            <div className="absolute right-3 top-1/2 -translate-y-1/2">
                                <Loader2 className="w-4 h-4 animate-spin text-muted-foreground" />
                            </div>
                        )}
                    </div>
                    <Button
                        type="submit"
                        disabled={!command.trim() || isExecuting}
                        isLoading={isExecuting}
                    >
                        <Send className="w-4 h-4 mr-2" />
                        Execute
                    </Button>
                </form>
                {/* Quick Commands */}
                {!currentSessionId && (
                    <div className="mt-3 flex flex-wrap gap-2">
                        <span className="text-xs text-muted-foreground mr-2">Quick commands:</span>
                        {[
                            'Create a new agent',
                            'List all tools',
                            'Show system status',
                            'Generate documentation'
                        ].map((quickCmd) => (
                            <Badge
                                key={quickCmd}
                                variant="secondary"
                                className="cursor-pointer hover:bg-secondary/80 transition-colors"
                                onClick={() => setCommand(quickCmd)}
                            >
                                {quickCmd}
                            </Badge>
                        ))}
                    </div>
                )}
            </div>

            {/* Command History */}
            <div className="flex-1 overflow-hidden flex flex-col">
                <div className="flex items-center justify-between px-4 py-2 border-b border-border bg-muted/30">
                    <div className="flex items-center gap-2">
                        <History className="w-4 h-4 text-muted-foreground" />
                        <span className="font-medium text-sm">Command History</span>
                    </div>
                    {commandHistory.length > 0 && (
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setCommandHistory([])}
                            className="text-xs"
                        >
                            Clear
                        </Button>
                    )}
                </div>

                <ScrollArea className="flex-1 p-4">
                    {commandHistory.length === 0 ? (
                        <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
                            <Terminal className="w-12 h-12 mb-3 opacity-50" />
                            <p className="text-sm">No commands executed yet</p>
                            <p className="text-xs mt-1">Start a session and enter a command</p>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {commandHistory.map((item) => (
                                <Card 
                                    key={item.id} 
                                    className={`cursor-pointer transition-all ${
                                        expandedCommands.has(item.id) ? 'ring-2 ring-primary' : ''
                                    }`}
                                    onClick={() => toggleCommandExpansion(item.id)}
                                >
                                    <CardHeader className="py-3 px-4">
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center gap-3 overflow-hidden">
                                                <StatusBadge status={item.status} />
                                                <span className="font-mono text-sm truncate max-w-[300px]">
                                                    {item.command}
                                                </span>
                                            </div>
                                            <div className="flex items-center gap-2">
                                                <span className="text-xs text-muted-foreground">
                                                    {formatExecutionTime(item.executionTime)}
                                                </span>
                                                {expandedCommands.has(item.id) ? (
                                                    <ChevronUp className="w-4 h-4 text-muted-foreground" />
                                                ) : (
                                                    <ChevronDown className="w-4 h-4 text-muted-foreground" />
                                                )}
                                            </div>
                                        </div>
                                        {item.intent !== 'unknown' && (
                                            <p className="text-xs text-muted-foreground mt-1">
                                                Intent: {item.intent}
                                            </p>
                                        )}
                                    </CardHeader>
                                    
                                    {expandedCommands.has(item.id) && (
                                        <CardContent className="py-3 px-4 border-t border-border bg-muted/30">
                                            <div className="space-y-3">
                                                <div>
                                                    <p className="text-xs font-medium text-muted-foreground mb-1">
                                                        Full Command
                                                    </p>
                                                    <p className="text-sm font-mono bg-muted p-2 rounded">
                                                        {item.command}
                                                    </p>
                                                </div>
                                                
                                                {item.error && (
                                                    <div>
                                                        <p className="text-xs font-medium text-destructive mb-1">
                                                            Error
                                                        </p>
                                                        <p className="text-sm text-destructive bg-destructive/10 p-2 rounded">
                                                            {item.error}
                                                        </p>
                                                    </div>
                                                )}
                                                
                                                {item.result && (
                                                    <div>
                                                        <p className="text-xs font-medium text-muted-foreground mb-1">
                                                            Result
                                                        </p>
                                                        <pre className="text-xs bg-muted p-3 rounded overflow-auto max-h-[300px]">
                                                            {JSON.stringify(item.result, null, 2)}
                                                        </pre>
                                                    </div>
                                                )}
                                                
                                                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                                    <Clock className="w-3 h-3" />
                                                    <span>
                                                        Executed: {new Date(item.timestamp).toLocaleString()}
                                                    </span>
                                                    <span className="mx-1">•</span>
                                                    <span>
                                                        {formatExecutionTime(item.executionTime)}
                                                    </span>
                                                </div>
                                            </div>
                                        </CardContent>
                                    )}
                                </Card>
                            ))}
                        </div>
                    )}
                </ScrollArea>
            </div>

            {/* Loading overlay for session operations */}
            {(createSessionMutation.isPending || completeSessionMutation.isPending) && (
                <div className="absolute inset-0 bg-background/80 flex items-center justify-center z-10">
                    <div className="flex flex-col items-center gap-2">
                        <Loader2 className="w-6 h-6 animate-spin" />
                        <span className="text-sm text-muted-foreground">
                            {createSessionMutation.isPending ? 'Creating session...' : 'Completing session...'}
                        </span>
                    </div>
                </div>
            )}
        </div>
    );
};

export default FuzzyPanel;
