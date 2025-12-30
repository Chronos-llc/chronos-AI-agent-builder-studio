import React, { useState, useEffect, useRef } from 'react';
import { useWebSocket } from '../../hooks/useWebSocket';
import { LogEntry, LogFilter, LogExportFormat } from '../../types/logging';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { ScrollArea } from '../ui/scroll-area';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { Download, FileText, Search, Trash2, Filter, Clock, AlertCircle, Info, CheckCircle2 } from 'lucide-react';
import { DatePickerWithRange } from '../ui/date-range-picker';


interface LoggingPanelProps {
    agentId: string;
    sessionId?: string;
}

export function LoggingPanel({ agentId, sessionId }: LoggingPanelProps) {
    const [logEntries, setLogEntries] = useState<LogEntry[]>([]);
    const [filteredLogs, setFilteredLogs] = useState<LogEntry[]>([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [logLevelFilter, setLogLevelFilter] = useState('all');
    const [dateRange, setDateRange] = useState<{ from: Date; to: Date } | undefined>(undefined);
    const [contextFilter, setContextFilter] = useState('');
    const [isAutoScroll, setIsAutoScroll] = useState(true);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const logEndRef = useRef<HTMLDivElement>(null);
    const logSocket = useWebSocket(`ws://localhost:8000/ws/logs/${agentId}`);

    // Scroll to bottom when new logs arrive
    useEffect(() => {
        if (isAutoScroll) {
            logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
        }
    }, [logEntries]);

    // Handle incoming log messages
    useEffect(() => {
        if (!logSocket.message) return;

        try {
            const message = JSON.parse(logSocket.message);

            if (message.type === 'log_entry') {
                setLogEntries(prev => [...prev, message.data]);
            } else if (message.type === 'log_batch') {
                setLogEntries(prev => [...prev, ...message.data]);
            }
        } catch (err) {
            console.error('Error parsing log message:', err);
        }
    }, [logSocket.message]);

    // Apply filters
    useEffect(() => {
        const filtered = logEntries.filter(log => {
            // Search term filter
            const matchesSearch = searchTerm === '' ||
                log.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
                (log.context && log.context.toLowerCase().includes(searchTerm.toLowerCase())) ||
                (log.details && JSON.stringify(log.details).toLowerCase().includes(searchTerm.toLowerCase()));

            // Log level filter
            const matchesLevel = logLevelFilter === 'all' || log.level === logLevelFilter;

            // Context filter
            const matchesContext = contextFilter === '' ||
                (log.context && log.context.toLowerCase().includes(contextFilter.toLowerCase()));

            // Date range filter
            const matchesDate = !dateRange || (
                new Date(log.timestamp) >= dateRange.from &&
                new Date(log.timestamp) <= dateRange.to
            );

            return matchesSearch && matchesLevel && matchesContext && matchesDate;
        });

        setFilteredLogs(filtered);
    }, [logEntries, searchTerm, logLevelFilter, contextFilter, dateRange]);

    const clearLogs = () => {
        setLogEntries([]);
        setFilteredLogs([]);
    };

    const exportLogs = async (format: LogExportFormat) => {
        try {
            setIsLoading(true);
            setError(null);

            const response = await fetch(`http://localhost:8000/api/logs/export`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    agent_id: agentId,
                    session_id: sessionId,
                    format: format,
                    filters: {
                        search_term: searchTerm,
                        log_level: logLevelFilter,
                        context: contextFilter,
                        date_range: dateRange
                    }
                })
            });

            if (!response.ok) {
                throw new Error('Failed to export logs');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `logs-${agentId}-${new Date().toISOString()}.${format}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

        } catch (err) {
            console.error('Export error:', err);
            setError(err instanceof Error ? err.message : 'Unknown error during export');
        } finally {
            setIsLoading(false);
        }
    };

    const getLogLevelIcon = (level: string) => {
        switch (level) {
            case 'error': return <AlertCircle className="w-4 h-4" />;
            case 'warning': return <AlertCircle className="w-4 h-4" />;
            case 'info': return <Info className="w-4 h-4" />;
            case 'debug': return <FileText className="w-4 h-4" />;
            case 'success': return <CheckCircle2 className="w-4 h-4" />;
            default: return <FileText className="w-4 h-4" />;
        }
    };

    const getLogLevelColor = (level: string) => {
        switch (level) {
            case 'error': return 'bg-red-500';
            case 'warning': return 'bg-yellow-500';
            case 'info': return 'bg-blue-500';
            case 'debug': return 'bg-gray-500';
            case 'success': return 'bg-green-500';
            default: return 'bg-purple-500';
        }
    };

    const toggleAutoScroll = () => {
        setIsAutoScroll(!isAutoScroll);
    };

    return (
        <div className="flex flex-col h-full bg-gray-900 text-white">
            <div className="p-4 border-b border-gray-700">
                <h2 className="text-xl font-bold flex items-center gap-2">
                    <FileText className="w-5 h-5" />
                    Comprehensive Logging System
                </h2>
            </div>

            <div className="p-4 border-b border-gray-700 bg-gray-800">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
                    <div>
                        <label className="text-sm text-gray-400 block mb-1">Search</label>
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                            <Input
                                placeholder="Search logs..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="pl-10 bg-gray-700"
                            />
                        </div>
                    </div>

                    <div>
                        <label className="text-sm text-gray-400 block mb-1">Log Level</label>
                        <Select value={logLevelFilter} onValueChange={setLogLevelFilter}>
                            <SelectTrigger className="bg-gray-700">
                                <SelectValue placeholder="All Levels" />
                            </SelectTrigger>
                            <SelectContent className="bg-gray-800">
                                <SelectItem value="all">All Levels</SelectItem>
                                <SelectItem value="error">Error</SelectItem>
                                <SelectItem value="warning">Warning</SelectItem>
                                <SelectItem value="info">Info</SelectItem>
                                <SelectItem value="debug">Debug</SelectItem>
                                <SelectItem value="success">Success</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>

                    <div>
                        <label className="text-sm text-gray-400 block mb-1">Context</label>
                        <Input
                            placeholder="Filter by context..."
                            value={contextFilter}
                            onChange={(e) => setContextFilter(e.target.value)}
                            className="bg-gray-700"
                        />
                    </div>
                </div>

                <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4 items-end">
                    <div>
                        <label className="text-sm text-gray-400 block mb-1">Date Range</label>
                        <DatePickerWithRange
                            date={dateRange}
                            onDateChange={setDateRange}
                            className="bg-gray-700"
                        />
                    </div>

                    <div className="flex gap-2 justify-end">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={toggleAutoScroll}
                            className={`bg-gray-700 hover:bg-gray-600 ${isAutoScroll ? 'border-blue-500' : ''}`}
                        >
                            <Clock className="w-4 h-4 mr-2" />
                            {isAutoScroll ? 'Auto Scroll ON' : 'Auto Scroll OFF'}
                        </Button>

                        <Button
                            variant="outline"
                            size="sm"
                            onClick={clearLogs}
                            className="bg-gray-700 hover:bg-gray-600"
                        >
                            <Trash2 className="w-4 h-4 mr-2" />
                            Clear Logs
                        </Button>

                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => exportLogs('json')}
                            disabled={isLoading}
                            className="bg-gray-700 hover:bg-gray-600"
                        >
                            <Download className="w-4 h-4 mr-2" />
                            Export JSON
                        </Button>

                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => exportLogs('csv')}
                            disabled={isLoading}
                            className="bg-gray-700 hover:bg-gray-600"
                        >
                            <Download className="w-4 h-4 mr-2" />
                            Export CSV
                        </Button>
                    </div>
                </div>
            </div>

            <div className="flex-1 overflow-hidden">
                <Card className="h-full bg-gray-800 border-gray-700 m-4">
                    <CardHeader>
                        <CardTitle>Log Entries ({filteredLogs.length} of {logEntries.length})</CardTitle>
                        {error && (
                            <div className="text-red-500 text-sm mt-2">
                                {error}
                            </div>
                        )}
                    </CardHeader>

                    <CardContent className="h-[calc(100%-80px)]">
                        <ScrollArea className="h-full pr-4">
                            {filteredLogs.length === 0 ? (
                                <div className="text-gray-500 text-center py-8">
                                    <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
                                    <p>No logs found matching current filters</p>
                                </div>
                            ) : (
                                <div className="space-y-2">
                                    {filteredLogs.map((log, index) => (
                                        <div key={index} className="p-3 border border-gray-700 rounded hover:bg-gray-700 transition-colors">
                                            <div className="flex items-start gap-3">
                                                <div className="flex-shrink-0">
                                                    <Badge className={getLogLevelColor(log.level)}>
                                                        {getLogLevelIcon(log.level)}
                                                        <span className="ml-1">{log.level.toUpperCase()}</span>
                                                    </Badge>
                                                </div>

                                                <div className="flex-1 min-w-0">
                                                    <div className="flex items-center gap-2 mb-1">
                                                        <span className="text-xs text-gray-400">
                                                            {new Date(log.timestamp).toLocaleString()}
                                                        </span>
                                                        {log.context && (
                                                            <span className="text-xs bg-gray-600 px-2 py-1 rounded">
                                                                {log.context}
                                                            </span>
                                                        )}
                                                    </div>

                                                    <div className="text-sm break-words">
                                                        {log.message}
                                                    </div>

                                                    {log.details && (
                                                        <div className="mt-2 text-xs text-gray-400">
                                                            <pre className="overflow-x-auto max-w-full">
                                                                {JSON.stringify(log.details, null, 2)}
                                                            </pre>
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                            <div ref={logEndRef} />
                        </ScrollArea>
                    </CardContent>
                </Card>
            </div>

            <div className="p-4 border-t border-gray-700 flex justify-between items-center">
                <div className="flex gap-2">
                    <Badge variant="outline" className="border-gray-600">
                        Total: {logEntries.length}
                    </Badge>
                    <Badge variant="outline" className="border-gray-600">
                        Filtered: {filteredLogs.length}
                    </Badge>
                    <Badge variant="outline" className={logSocket.readyState === WebSocket.OPEN ? 'border-green-500 text-green-500' : 'border-red-500 text-red-500'}>
                        {logSocket.readyState === WebSocket.OPEN ? 'Connected' : 'Disconnected'}
                    </Badge>
                </div>

                <div className="flex gap-2">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => exportLogs('json')}
                        disabled={isLoading}
                        className="bg-gray-700 hover:bg-gray-600"
                    >
                        <Download className="w-4 h-4 mr-2" />
                        Export All
                    </Button>
                </div>
            </div>
        </div>
    );
}