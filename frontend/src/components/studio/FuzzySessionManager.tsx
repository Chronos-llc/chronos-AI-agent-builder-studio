/**
 * FuzzySessionManager - Session Management Component for Meta-Agent FUZZY
 * 
 * Provides session creation, management, history display,
 * and context preservation between commands.
 */
import React, { useState, useCallback } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import {
    FolderOpen,
    Plus,
    Clock,
    CheckCircle,
    XCircle,
    History,
    ChevronRight,
    Trash2,
    Archive,
    RefreshCw,
    Calendar
} from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { ScrollArea } from '../ui/scroll-area';
import metaAgentService from '../../services/metaAgentService';
import type {
    MetaAgentSession,
    SessionContext,
    CommandHistoryEntry
} from '../../types/metaAgent';
import { SessionStatus } from '../../types/metaAgent';

// ============== Helper Components ==============

const SessionItem: React.FC<{
    session: MetaAgentSession;
    isSelected: boolean;
    onSelect: () => void;
    onComplete: () => void;
    onDelete: () => void;
}> = ({ session, isSelected, onSelect, onComplete, onDelete }) => {
    const getStatusConfig = (status: SessionStatus) => {
        switch (status) {
            case SessionStatus.ACTIVE:
                return { color: 'bg-green-100 text-green-800', icon: CheckCircle, label: 'Active' };
            case SessionStatus.COMPLETED:
                return { color: 'bg-blue-100 text-blue-800', icon: Archive, label: 'Completed' };
            case SessionStatus.TIMEOUT:
                return { color: 'bg-red-100 text-red-800', icon: XCircle, label: 'Timeout' };
            default:
                return { color: 'bg-gray-100 text-gray-800', icon: Clock, label: status };
        }
    };

    const config = getStatusConfig(session.status);
    const Icon = config.icon;

    return (
        <div
            className={`p-3 rounded-lg border cursor-pointer transition-all ${
                isSelected
                    ? 'border-primary bg-primary/5'
                    : 'border-border hover:border-primary/50 hover:bg-muted/50'
            }`}
            onClick={onSelect}
        >
            <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                    <Icon className="w-4 h-4 text-muted-foreground" />
                    <span className="font-mono text-xs">{session.id.slice(0, 8)}...</span>
                    <Badge variant="secondary" className={`text-xs ${config.color}`}>
                        {config.label}
                    </Badge>
                </div>
                {session.status === SessionStatus.ACTIVE && (
                    <div className="flex items-center gap-1">
                        <Button
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6"
                            onClick={(e) => {
                                e.stopPropagation();
                                onComplete();
                            }}
                            title="Complete session"
                        >
                            <CheckCircle className="w-3 h-3" />
                        </Button>
                        <Button
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6 text-destructive"
                            onClick={(e) => {
                                e.stopPropagation();
                                onDelete();
                            }}
                            title="Delete session"
                        >
                            <Trash2 className="w-3 h-3" />
                        </Button>
                    </div>
                )}
            </div>
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <Calendar className="w-3 h-3" />
                <span>{new Date(session.created_at).toLocaleDateString()}</span>
                <span className="mx-1">•</span>
                <span>{new Date(session.created_at).toLocaleTimeString()}</span>
            </div>
            {session.context?.history && (
                <div className="mt-2 text-xs text-muted-foreground">
                    <span>{session.context.history.length} commands</span>
                </div>
            )}
        </div>
    );
};

const ContextViewer: React.FC<{ context: SessionContext }> = ({ context }) => {
    return (
        <div className="space-y-3">
            {context.history.length === 0 ? (
                <div className="text-center py-4 text-muted-foreground">
                    <History className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">No command history</p>
                    <p className="text-xs mt-1">Commands will appear here as you execute them</p>
                </div>
            ) : (
                <div className="space-y-2">
                    {context.history.map((entry: CommandHistoryEntry, index: number) => (
                        <div
                            key={index}
                            className="p-2 rounded-md bg-muted/50 text-sm"
                        >
                            <div className="flex items-center justify-between mb-1">
                                <span className="font-mono text-xs truncate max-w-[150px]">
                                    {entry.command}
                                </span>
                                <span className="text-xs text-muted-foreground">
                                    {new Date(entry.timestamp).toLocaleTimeString()}
                                </span>
                            </div>
                            <p className="text-xs text-muted-foreground">
                                Intent: {entry.intent}
                            </p>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

// ============== Main Component ==============

interface FuzzySessionManagerProps {
    defaultMetaAgentId?: number;
    onSessionSelect?: (sessionId: string) => void;
}

export const FuzzySessionManager: React.FC<FuzzySessionManagerProps> = ({
    defaultMetaAgentId = 1,
    onSessionSelect
}) => {
    const queryClient = useQueryClient();
    const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);
    const [isCreatingSession, setIsCreatingSession] = useState(false);

    // Mock sessions for demo (in production, fetch from API)
    const [sessions, setSessions] = useState<MetaAgentSession[]>([
        {
            id: 'sess-001',
            user_id: 1,
            meta_agent_id: 1,
            status: SessionStatus.ACTIVE,
            context: {
                history: [
                    { command: 'List all agents', intent: 'list_agents', result: {}, timestamp: new Date().toISOString() }
                ]
            },
            created_at: new Date(Date.now() - 3600000).toISOString(),
            updated_at: new Date().toISOString()
        },
        {
            id: 'sess-002',
            user_id: 1,
            meta_agent_id: 1,
            status: SessionStatus.COMPLETED,
            context: {
                history: [
                    { command: 'Create new agent', intent: 'create_agent', result: {}, timestamp: new Date(Date.now() - 7200000).toISOString() },
                    { command: 'Test agent', intent: 'test_agent', result: {}, timestamp: new Date(Date.now() - 7000000).toISOString() }
                ]
            },
            created_at: new Date(Date.now() - 7200000).toISOString(),
            updated_at: new Date(Date.now() - 7000000).toISOString(),
            completed_at: new Date(Date.now() - 7000000).toISOString()
        }
    ]);

    // Create session mutation
    const createSessionMutation = useMutation({
        mutationFn: async () => {
            const newSession = await metaAgentService.createSession(defaultMetaAgentId);
            return newSession;
        },
        onSuccess: (newSession: MetaAgentSession) => {
            setSessions(prev => [newSession, ...prev]);
            setSelectedSessionId(newSession.id);
            setIsCreatingSession(false);
            toast.success('Session created');
            queryClient.invalidateQueries({ queryKey: ['meta-agent-sessions'] });
        },
        onError: () => {
            // For demo, create a mock session if API fails
            const mockSession: MetaAgentSession = {
                id: `sess-${Date.now()}`,
                user_id: 1,
                meta_agent_id: defaultMetaAgentId,
                status: SessionStatus.ACTIVE,
                context: { history: [] },
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString()
            };
            setSessions(prev => [mockSession, ...prev]);
            setSelectedSessionId(mockSession.id);
            setIsCreatingSession(false);
            toast.success('Session created (demo mode)');
        },
    });

    // Complete session mutation
    const completeSessionMutation = useMutation({
        mutationFn: async (sessionId: string) => {
            await metaAgentService.completeSession(sessionId);
        },
        onSuccess: (_, sessionId: string) => {
            setSessions(prev =>
                prev.map(s =>
                    s.id === sessionId
                        ? { ...s, status: SessionStatus.COMPLETED, completed_at: new Date().toISOString() }
                        : s
                )
            );
            toast.success('Session completed');
            queryClient.invalidateQueries({ queryKey: ['meta-agent-sessions'] });
        },
        onError: () => {
            toast.error('Failed to complete session');
        },
    });

    // Delete session mutation
    const deleteSessionMutation = useMutation({
        mutationFn: async (sessionId: string) => {
            // In production: await metaAgentService.deleteSession(sessionId);
            return sessionId;
        },
        onSuccess: (_, sessionId: string) => {
            setSessions(prev => prev.filter(s => s.id !== sessionId));
            if (selectedSessionId === sessionId) {
                setSelectedSessionId(null);
            }
            toast.success('Session deleted');
        },
        onError: () => {
            toast.error('Failed to delete session');
        },
    });

    // Handle session selection
    const handleSelectSession = useCallback((sessionId: string) => {
        setSelectedSessionId(sessionId);
        onSessionSelect?.(sessionId);
    }, [onSessionSelect]);

    // Handle session creation
    const handleCreateSession = useCallback(() => {
        setIsCreatingSession(true);
        createSessionMutation.mutate();
    }, [createSessionMutation]);

    // Handle session completion
    const handleCompleteSession = useCallback((sessionId: string) => {
        completeSessionMutation.mutate(sessionId);
    }, [completeSessionMutation]);

    // Handle session deletion
    const handleDeleteSession = useCallback((sessionId: string) => {
        if (confirm('Are you sure you want to delete this session?')) {
            deleteSessionMutation.mutate(sessionId);
        }
    }, [deleteSessionMutation]);

    // Get selected session
    const selectedSession = sessions.find(s => s.id === selectedSessionId);

    // Active sessions count
    const activeSessionsCount = sessions.filter(s => s.status === SessionStatus.ACTIVE).length;
    const completedSessionsCount = sessions.filter(s => s.status === SessionStatus.COMPLETED).length;

    return (
        <div className="flex flex-col h-full bg-background text-foreground">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-border">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                        <FolderOpen className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                        <h2 className="font-semibold">Session Manager</h2>
                        <p className="text-sm text-muted-foreground">
                            Manage your FUZZY sessions
                        </p>
                    </div>
                </div>
                <Button
                    size="sm"
                    onClick={handleCreateSession}
                    disabled={isCreatingSession || createSessionMutation.isPending}
                >
                    <Plus className="w-4 h-4 mr-1" />
                    New Session
                </Button>
            </div>

            {/* Session Stats */}
            <div className="px-4 py-2 border-b border-border bg-muted/30">
                <div className="flex items-center gap-4 text-sm">
                    <div className="flex items-center gap-1">
                        <div className="w-2 h-2 rounded-full bg-green-500" />
                        <span className="text-muted-foreground">Active:</span>
                        <span className="font-medium">{activeSessionsCount}</span>
                    </div>
                    <div className="flex items-center gap-1">
                        <div className="w-2 h-2 rounded-full bg-blue-500" />
                        <span className="text-muted-foreground">Completed:</span>
                        <span className="font-medium">{completedSessionsCount}</span>
                    </div>
                    <div className="flex items-center gap-1">
                        <div className="w-2 h-2 rounded-full bg-gray-400" />
                        <span className="text-muted-foreground">Total:</span>
                        <span className="font-medium">{sessions.length}</span>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 flex overflow-hidden">
                {/* Session List */}
                <div className="w-1/2 border-r border-border overflow-auto">
                    <div className="p-3 border-b border-border bg-muted/20">
                        <h3 className="font-medium text-sm flex items-center gap-2">
                            <History className="w-4 h-4" />
                            Sessions
                        </h3>
                    </div>
                    <ScrollArea className="h-[calc(100%-40px)] p-3">
                        <div className="space-y-2">
                            {sessions.length === 0 ? (
                                <div className="text-center py-8 text-muted-foreground">
                                    <FolderOpen className="w-8 h-8 mx-auto mb-2 opacity-50" />
                                    <p className="text-sm">No sessions yet</p>
                                    <Button
                                        variant="link"
                                        size="sm"
                                        onClick={handleCreateSession}
                                        className="mt-2"
                                    >
                                        Create your first session
                                    </Button>
                                </div>
                            ) : (
                                sessions.map((session) => (
                                    <SessionItem
                                        key={session.id}
                                        session={session}
                                        isSelected={selectedSessionId === session.id}
                                        onSelect={() => handleSelectSession(session.id)}
                                        onComplete={() => handleCompleteSession(session.id)}
                                        onDelete={() => handleDeleteSession(session.id)}
                                    />
                                ))
                            )}
                        </div>
                    </ScrollArea>
                </div>

                {/* Session Details */}
                <div className="w-1/2 flex flex-col overflow-hidden">
                    <div className="p-3 border-b border-border bg-muted/20">
                        <h3 className="font-medium text-sm flex items-center gap-2">
                            <ChevronRight className="w-4 h-4" />
                            Session Details
                        </h3>
                    </div>
                    <ScrollArea className="flex-1 p-4">
                        {selectedSession ? (
                            <div className="space-y-4">
                                {/* Session Info */}
                                <Card>
                                    <CardHeader className="py-3 px-4">
                                        <CardTitle className="text-sm flex items-center gap-2">
                                            Session: {selectedSession.id}
                                        </CardTitle>
                                    </CardHeader>
                                    <CardContent className="py-2 px-4 space-y-2">
                                        <div className="flex items-center justify-between text-sm">
                                            <span className="text-muted-foreground">Status</span>
                                            <Badge variant="outline">
                                                {selectedSession.status}
                                            </Badge>
                                        </div>
                                        <div className="flex items-center justify-between text-sm">
                                            <span className="text-muted-foreground">Created</span>
                                            <span>{new Date(selectedSession.created_at).toLocaleString()}</span>
                                        </div>
                                        <div className="flex items-center justify-between text-sm">
                                            <span className="text-muted-foreground">Updated</span>
                                            <span>{new Date(selectedSession.updated_at).toLocaleString()}</span>
                                        </div>
                                        {selectedSession.completed_at && (
                                            <div className="flex items-center justify-between text-sm">
                                                <span className="text-muted-foreground">Completed</span>
                                                <span>{new Date(selectedSession.completed_at).toLocaleString()}</span>
                                            </div>
                                        )}
                                    </CardContent>
                                </Card>

                                {/* Context */}
                                {selectedSession.context && (
                                    <Card>
                                        <CardHeader className="py-3 px-4">
                                            <CardTitle className="text-sm flex items-center gap-2">
                                                <History className="w-4 h-4" />
                                                Command History
                                            </CardTitle>
                                        </CardHeader>
                                        <CardContent className="py-2 px-4">
                                            <ContextViewer context={selectedSession.context} />
                                        </CardContent>
                                    </Card>
                                )}

                                {/* Actions */}
                                {selectedSession.status === SessionStatus.ACTIVE && (
                                    <div className="flex gap-2">
                                        <Button
                                            variant="outline"
                                            size="sm"
                                            onClick={() => handleCompleteSession(selectedSession.id)}
                                            className="flex-1"
                                        >
                                            <CheckCircle className="w-4 h-4 mr-1" />
                                            Complete Session
                                        </Button>
                                        <Button
                                            variant="destructive"
                                            size="sm"
                                            onClick={() => handleDeleteSession(selectedSession.id)}
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </Button>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
                                <FolderOpen className="w-12 h-12 mb-3 opacity-50" />
                                <p className="text-sm">Select a session to view details</p>
                            </div>
                        )}
                    </ScrollArea>
                </div>
            </div>

            {/* Loading overlay */}
            {(createSessionMutation.isPending || completeSessionMutation.isPending || deleteSessionMutation.isPending) && (
                <div className="absolute inset-0 bg-background/80 flex items-center justify-center z-10">
                    <div className="flex flex-col items-center gap-2">
                        <RefreshCw className="w-6 h-6 animate-spin" />
                        <span className="text-sm text-muted-foreground">Processing...</span>
                    </div>
                </div>
            )}
        </div>
    );
};

export default FuzzySessionManager;
