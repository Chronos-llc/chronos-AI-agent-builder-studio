/**
 * FuzzyCommandHistory - Command History Component for Meta-Agent FUZZY
 * 
 * Displays list of commands with status indicators, expandable details,
 * result preview, and full result modal.
 */
import React, { useState, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import {
    History,
    Clock,
    CheckCircle,
    XCircle,
    AlertCircle,
    ChevronDown,
    ChevronUp,
    Copy,
    Search,
    Filter,
    Terminal,
    Loader2,
    Eye
} from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Card, CardContent, CardHeader } from '../ui/card';
import { Badge } from '../ui/badge';
import { ScrollArea } from '../ui/scroll-area';
import metaAgentService from '../../services/metaAgentService';
import type {
    MetaAgentCommand,
    CommandFilters,
    CommandListResponse
} from '../../types/metaAgent';
import { CommandStatus } from '../../types/metaAgent';

// ============== Helper Components ==============

const StatusIndicator: React.FC<{ status: CommandStatus }> = ({ status }) => {
    const getStatusConfig = (status: CommandStatus) => {
        switch (status) {
            case 'completed':
                return { color: 'text-green-500', bg: 'bg-green-500', icon: CheckCircle, label: 'Success' };
            case 'executing':
                return { color: 'text-yellow-500', bg: 'bg-yellow-500', icon: Clock, iconClass: 'animate-spin', label: 'Running' };
            case 'pending':
                return { color: 'text-blue-500', bg: 'bg-blue-500', icon: Clock, label: 'Pending' };
            case 'failed':
                return { color: 'text-red-500', bg: 'bg-red-500', icon: XCircle, label: 'Failed' };
            default:
                return { color: 'text-gray-500', bg: 'bg-gray-500', icon: AlertCircle, label: status };
        }
    };

    const config = getStatusConfig(status);
    const Icon = config.icon;

    return (
        <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${config.bg}`} />
            <Icon className={`w-4 h-4 ${config.color} ${config.iconClass || ''}`} />
            <span className={`text-sm ${config.color}`}>{config.label}</span>
        </div>
    );
};

const ResultPreview: React.FC<{ result?: Record<string, unknown>; maxHeight?: 'sm' | 'md' | 'lg' | 'xl' }> = ({
    result,
    maxHeight = 'sm'
}) => {
    if (!result) {
        return <span className="text-muted-foreground text-sm">No result</span>;
    }

    const preview = JSON.stringify(result, null, 2);
    
    // Map predefined height options to Tailwind classes
    const heightClass = {
        sm: 'max-h-[100px]',
        md: 'max-h-[150px]',
        lg: 'max-h-[200px]',
        xl: 'max-h-[300px]'
    }[maxHeight];

    return (
        <pre
            className={`text-xs bg-muted p-2 rounded overflow-hidden ${heightClass}`}
        >
            {preview.length > 200 ? preview.slice(0, 200) + '...' : preview}
        </pre>
    );
};

// ============== Result Modal ==============

interface ResultModalProps {
    isOpen: boolean;
    onClose: () => void;
    command: MetaAgentCommand;
}

const ResultModal: React.FC<ResultModalProps> = ({ isOpen, onClose, command }) => {
    const [copied, setCopied] = useState(false);

    const handleCopy = useCallback(() => {
        const content = JSON.stringify(command.result || {}, null, 2);
        navigator.clipboard.writeText(content);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    }, [command.result]);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-card border border-border rounded-lg w-full max-w-2xl max-h-[80vh] flex flex-col">
                <div className="flex items-center justify-between p-4 border-b border-border">
                    <div className="flex items-center gap-2">
                        <Terminal className="w-5 h-5" />
                        <h3 className="font-semibold">Command Result</h3>
                        <Badge variant="outline" className="ml-2">
                            ID: {command.id}
                        </Badge>
                    </div>
                    <div className="flex items-center gap-2">
                        <Button variant="ghost" size="icon" onClick={handleCopy}>
                            <Copy className="w-4 h-4" />
                        </Button>
                        <Button variant="ghost" size="icon" onClick={onClose}>
                            <XCircle className="w-4 h-4" />
                        </Button>
                    </div>
                </div>

                <div className="flex-1 overflow-auto p-4">
                    <div className="space-y-4">
                        {/* Command Info */}
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <p className="text-xs text-muted-foreground mb-1">Command</p>
                                <p className="font-mono text-sm bg-muted p-2 rounded">
                                    {command.command_type}
                                </p>
                            </div>
                            <div>
                                <p className="text-xs text-muted-foreground mb-1">Intent</p>
                                <p className="text-sm">{command.intent}</p>
                            </div>
                            <div>
                                <p className="text-xs text-muted-foreground mb-1">Status</p>
                                <StatusIndicator status={command.status} />
                            </div>
                            <div>
                                <p className="text-xs text-muted-foreground mb-1">Execution Time</p>
                                <p className="text-sm">
                                    {command.execution_time_ms
                                        ? command.execution_time_ms < 1000
                                            ? `${command.execution_time_ms.toFixed(0)}ms`
                                            : `${(command.execution_time_ms / 1000).toFixed(2)}s`
                                        : 'N/A'}
                                </p>
                            </div>
                            <div>
                                <p className="text-xs text-muted-foreground mb-1">Created</p>
                                <p className="text-sm">{new Date(command.created_at).toLocaleString()}</p>
                            </div>
                            <div>
                                <p className="text-xs text-muted-foreground mb-1">Session ID</p>
                                <p className="font-mono text-sm">{command.session_id || 'N/A'}</p>
                            </div>
                        </div>

                        {/* Parameters */}
                        {command.parameters && Object.keys(command.parameters).length > 0 && (
                            <div>
                                <p className="text-xs text-muted-foreground mb-1">Parameters</p>
                                <pre className="text-xs bg-muted p-3 rounded overflow-auto max-h-[150px]">
                                    {JSON.stringify(command.parameters, null, 2)}
                                </pre>
                            </div>
                        )}

                        {/* Error Message */}
                        {command.error_message && (
                            <div>
                                <p className="text-xs text-muted-foreground mb-1">Error</p>
                                <p className="text-sm text-destructive bg-destructive/10 p-3 rounded">
                                    {command.error_message}
                                </p>
                            </div>
                        )}

                        {/* Result */}
                        {command.result && (
                            <div>
                                <div className="flex items-center justify-between mb-1">
                                    <p className="text-xs text-muted-foreground">Result</p>
                                    <span className="text-xs text-muted-foreground">
                                        {copied ? 'Copied!' : 'Click copy to clipboard'}
                                    </span>
                                </div>
                                <pre className="text-xs bg-muted p-3 rounded overflow-auto max-h-[300px]">
                                    {JSON.stringify(command.result, null, 2)}
                                </pre>
                            </div>
                        )}
                    </div>
                </div>

                <div className="border-t border-border p-4 flex justify-end">
                    <Button variant="outline" onClick={onClose}>
                        Close
                    </Button>
                </div>
            </div>
        </div>
    );
};

// ============== Command List Item ==============

interface CommandListItemProps {
    command: MetaAgentCommand;
    isExpanded: boolean;
    onToggleExpand: () => void;
    onViewResult: () => void;
}

const CommandListItem: React.FC<CommandListItemProps> = ({
    command,
    isExpanded,
    onToggleExpand,
    onViewResult
}) => {
    const formatExecutionTime = (ms?: number): string => {
        if (!ms) return 'N/A';
        if (ms < 1000) return `${ms.toFixed(0)}ms`;
        if (ms < 60000) return `${(ms / 1000).toFixed(2)}s`;
        return `${(ms / 60000).toFixed(2)}m`;
    };

    return (
        <Card
            className={`cursor-pointer transition-all ${
                isExpanded ? 'ring-2 ring-primary' : 'hover:border-primary/50'
            }`}
            onClick={onToggleExpand}
        >
            <CardHeader className="py-3 px-4">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3 overflow-hidden">
                        <StatusIndicator status={command.status} />
                        <div className="flex-1 overflow-hidden">
                            <p className="font-mono text-sm truncate" title={command.command_type}>
                                {command.command_type}
                            </p>
                            <p className="text-xs text-muted-foreground">
                                Intent: {command.intent}
                            </p>
                        </div>
                    </div>
                    <div className="flex items-center gap-3">
                        <span className="text-xs text-muted-foreground">
                            {formatExecutionTime(command.execution_time_ms)}
                        </span>
                        {command.result && (
                            <Button
                                variant="ghost"
                                size="icon"
                                className="h-8 w-8"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    onViewResult();
                                }}
                                title="View full result"
                            >
                                <Eye className="w-4 h-4" />
                            </Button>
                        )}
                        {isExpanded ? (
                            <ChevronUp className="w-4 h-4 text-muted-foreground" />
                        ) : (
                            <ChevronDown className="w-4 h-4 text-muted-foreground" />
                        )}
                    </div>
                </div>
            </CardHeader>

            {isExpanded && (
                <CardContent className="py-3 px-4 border-t border-border bg-muted/30">
                    <div className="space-y-3">
                        <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                                <p className="text-xs text-muted-foreground mb-1">Command Type</p>
                                <p className="font-mono">{command.command_type}</p>
                            </div>
                            <div>
                                <p className="text-xs text-muted-foreground mb-1">Intent</p>
                                <p>{command.intent}</p>
                            </div>
                            <div>
                                <p className="text-xs text-muted-foreground mb-1">Session ID</p>
                                <p className="font-mono text-xs">{command.session_id || 'N/A'}</p>
                            </div>
                            <div>
                                <p className="text-xs text-muted-foreground mb-1">Created</p>
                                <p>{new Date(command.created_at).toLocaleString()}</p>
                            </div>
                        </div>

                        {command.parameters && Object.keys(command.parameters).length > 0 && (
                            <div>
                                <p className="text-xs text-muted-foreground mb-1">Parameters</p>
                                <pre className="text-xs bg-muted p-2 rounded overflow-auto max-h-[100px]">
                                    {JSON.stringify(command.parameters, null, 2)}
                                </pre>
                            </div>
                        )}

                        {command.error_message && (
                            <div className="p-2 rounded bg-destructive/10 border border-destructive/20">
                                <p className="text-xs text-muted-foreground mb-1">Error</p>
                                <p className="text-sm text-destructive">{command.error_message}</p>
                            </div>
                        )}

                        {command.result && (
                            <div>
                                <p className="text-xs text-muted-foreground mb-1">Result Preview</p>
                                <ResultPreview result={command.result} maxHeight="sm" />
                            </div>
                        )}

                        <div className="flex items-center justify-between text-xs text-muted-foreground">
                            <span>ID: {command.id}</span>
                            <span>Execution: {formatExecutionTime(command.execution_time_ms)}</span>
                        </div>
                    </div>
                </CardContent>
            )}
        </Card>
    );
};

// ============== Main Component ==============

interface FuzzyCommandHistoryProps {
    sessionId?: string;
    filters?: CommandFilters;
    onCommandSelect?: (commandId: number) => void;
}

export const FuzzyCommandHistory: React.FC<FuzzyCommandHistoryProps> = ({
    sessionId,
    filters
}) => {
    const [searchQuery, setSearchQuery] = useState('');
    const [statusFilter, setStatusFilter] = useState<CommandStatus | 'all'>('all');
    const [expandedCommands, setExpandedCommands] = useState<Set<number>>(new Set());
    const [selectedCommand, setSelectedCommand] = useState<MetaAgentCommand | null>(null);

    // Fetch commands
    const {
        data: commandData,
        isLoading,
        error,
        refetch
    } = useQuery<CommandListResponse>({
        queryKey: ['meta-agent-commands', sessionId, filters],
        queryFn: async () => {
            const params: CommandFilters = {
                ...filters,
                session_id: sessionId,
                status: statusFilter !== 'all' ? statusFilter : undefined,
                limit: 100,
                offset: 0
            };
            try {
                return await metaAgentService.listCommands(params);
            } catch (err: unknown) {
                toast.error('Failed to load commands');
                console.error('Error fetching commands:', err);
                throw err;
            }
        }
    });

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

    // Filter commands by search query
    const filteredCommands = commandData?.commands.filter(cmd =>
        cmd.command_type.toLowerCase().includes(searchQuery.toLowerCase()) ||
        cmd.intent.toLowerCase().includes(searchQuery.toLowerCase())
    ) || [];

    // Handle view result
    const handleViewResult = useCallback((command: MetaAgentCommand) => {
        setSelectedCommand(command);
    }, []);

    // Get unique statuses for filter
    const statuses: (CommandStatus | 'all')[] = ['all', CommandStatus.PENDING, CommandStatus.EXECUTING, CommandStatus.COMPLETED, CommandStatus.FAILED];

    return (
        <div className="flex flex-col h-full bg-background text-foreground">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-border">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                        <History className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                        <h2 className="font-semibold">Command History</h2>
                        <p className="text-sm text-muted-foreground">
                            {commandData?.total || 0} commands
                        </p>
                    </div>
                </div>
                <Button variant="outline" size="sm" onClick={() => refetch()}>
                    <Clock className="w-4 h-4 mr-1" />
                    Refresh
                </Button>
            </div>

            {/* Filters */}
            <div className="p-4 border-b border-border bg-muted/30">
                <div className="flex items-center gap-3">
                    <div className="relative flex-1">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                        <Input
                            type="text"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            placeholder="Search commands..."
                            className="pl-9"
                        />
                    </div>
                    <div className="flex items-center gap-2">
                        <Filter className="w-4 h-4 text-muted-foreground" />
                        <select
                            value={statusFilter}
                            onChange={(e) => setStatusFilter(e.target.value as CommandStatus | 'all')}
                            className="px-3 py-2 border border-input rounded-md bg-background text-sm"
                            aria-label="Filter by status"
                        >
                            {statuses.map(status => (
                                <option key={status} value={status}>
                                    {status === 'all' ? 'All Status' : status.charAt(0).toUpperCase() + status.slice(1)}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>
            </div>

            {/* Command List */}
            <ScrollArea className="flex-1 p-4">
                {isLoading ? (
                    <div className="flex items-center justify-center h-full">
                        <div className="flex flex-col items-center gap-2">
                            <Loader2 className="w-6 h-6 animate-spin" />
                            <span className="text-sm text-muted-foreground">Loading commands...</span>
                        </div>
                    </div>
                ) : error ? (
                    <div className="flex flex-col items-center justify-center h-full text-destructive">
                        <AlertCircle className="w-8 h-8 mb-2" />
                        <p className="text-sm">Failed to load commands</p>
                        <Button
                            variant="link"
                            size="sm"
                            onClick={() => refetch()}
                            className="mt-2"
                        >
                            Retry
                        </Button>
                    </div>
                ) : filteredCommands.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
                        <History className="w-12 h-12 mb-3 opacity-50" />
                        <p className="text-sm">No commands found</p>
                        {searchQuery && (
                            <p className="text-xs mt-1">Try adjusting your search</p>
                        )}
                    </div>
                ) : (
                    <div className="space-y-3">
                        {filteredCommands.map((command) => (
                            <CommandListItem
                                key={command.id}
                                command={command}
                                isExpanded={expandedCommands.has(command.id)}
                                onToggleExpand={() => toggleCommandExpansion(command.id)}
                                onViewResult={() => handleViewResult(command)}
                            />
                        ))}
                    </div>
                )}
            </ScrollArea>

            {/* Footer */}
            <div className="p-4 border-t border-border bg-muted/30 text-xs text-muted-foreground">
                <div className="flex items-center justify-between">
                    <span>Showing {filteredCommands.length} of {commandData?.total || 0} commands</span>
                    <div className="flex items-center gap-4">
                        <span className="flex items-center gap-1">
                            <CheckCircle className="w-3 h-3 text-green-500" />
                            {commandData?.commands.filter(c => c.status === 'completed').length || 0}
                        </span>
                        <span className="flex items-center gap-1">
                            <XCircle className="w-3 h-3 text-red-500" />
                            {commandData?.commands.filter(c => c.status === 'failed').length || 0}
                        </span>
                    </div>
                </div>
            </div>

            {/* Result Modal */}
            {selectedCommand && (
                <ResultModal
                    isOpen={!!selectedCommand}
                    onClose={() => setSelectedCommand(null)}
                    command={selectedCommand}
                />
            )}
        </div>
    );
};

export default FuzzyCommandHistory;
