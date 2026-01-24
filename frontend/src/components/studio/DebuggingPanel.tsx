import { useState, useEffect, useRef } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { DebugEvent, LogEntry, ExecutionTrace, BreakpointHit, WatchExpressionResult } from '@/types/debugging';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { ScrollArea } from '../ui/scroll-area';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { Terminal } from 'lucide-react';


interface DebuggingPanelProps {
  agentId: string;
  sessionId: string;
}

export function DebuggingPanel({ agentId, sessionId }: DebuggingPanelProps) {
  const [logEntries, setLogEntries] = useState<LogEntry[]>([]);
  const [executionTraces, setExecutionTraces] = useState<ExecutionTrace[]>([]);
  const [breakpoints, setBreakpoints] = useState<BreakpointHit[]>([]);
  const [watchExpressions, setWatchExpressions] = useState<WatchExpressionResult[]>([]);
  const [debugEvents, setDebugEvents] = useState<DebugEvent[]>([]);
  const [isDebugging, setIsDebugging] = useState(false);
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [watchExpressionInput, setWatchExpressionInput] = useState('');
  const [logLevelFilter, setLogLevelFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  
  const logEndRef = useRef<HTMLDivElement>(null);
  
  // WebSocket connections
  const debugSocket = useWebSocket(`ws://localhost:8000/ws/debug/${sessionId}`);
  const logSocket = useWebSocket(`ws://localhost:8000/ws/logs/${agentId}`);
  const performanceSocket = useWebSocket(`ws://localhost:8000/ws/performance/${sessionId}`);
  
  // Scroll to bottom of logs
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logEntries]);
  
  // Handle incoming debug messages
  useEffect(() => {
    if (!debugSocket.lastMessage) return;
    
    const message = JSON.parse(debugSocket.lastMessage.data);
    
    switch (message.type) {
      case 'log_entry':
        setLogEntries(prev => [...prev, message.data]);
        break;
      case 'execution_trace':
        setExecutionTraces(prev => [...prev, message.data]);
        break;
      case 'breakpoint_hit':
        setBreakpoints(prev => [...prev, message.data]);
        break;
      case 'watch_result':
        setWatchExpressions(prev => [...prev, message.data]);
        break;
      case 'debug_event':
        setDebugEvents(prev => [...prev, message.data]);
        break;
      case 'command_response':
        console.log('Command response:', message.data);
        break;
    }
  }, [debugSocket.lastMessage]);
  
  // Handle incoming log messages
  useEffect(() => {
    if (!logSocket.lastMessage) return;
    
    const message = JSON.parse(logSocket.lastMessage.data);
    
    if (message.type === 'log_entry') {
      setLogEntries(prev => [...prev, message.data]);
    }
  }, [logSocket.lastMessage]);
  
  const startDebugging = () => {
    if (debugSocket.readyState === WebSocket.OPEN) {
      debugSocket.send(JSON.stringify({
        type: 'command',
        data: {
          command: 'start_debugging',
          session_id: sessionId
        }
      }));
      setIsDebugging(true);
    }
  };
  
  const stopDebugging = () => {
    if (debugSocket.readyState === WebSocket.OPEN) {
      debugSocket.send(JSON.stringify({
        type: 'command',
        data: {
          command: 'stop_debugging',
          session_id: sessionId
        }
      }));
      setIsDebugging(false);
    }
  };
  
  const startMonitoring = () => {
    if (performanceSocket.readyState === WebSocket.OPEN) {
      performanceSocket.send(JSON.stringify({
        type: 'monitor_start',
        data: {
          session_id: sessionId
        }
      }));
      setIsMonitoring(true);
    }
  };
  
  const stopMonitoring = () => {
    if (performanceSocket.readyState === WebSocket.OPEN) {
      performanceSocket.send(JSON.stringify({
        type: 'monitor_stop',
        data: {
          session_id: sessionId
        }
      }));
      setIsMonitoring(false);
    }
  };
  
  const addWatchExpression = () => {
    if (!watchExpressionInput.trim()) return;
    
    if (debugSocket.readyState === WebSocket.OPEN) {
      debugSocket.send(JSON.stringify({
        type: 'command',
        data: {
          command: 'add_watch',
          expression: watchExpressionInput,
          session_id: sessionId
        }
      }));
      setWatchExpressionInput('');
    }
  };
  
  const clearLogs = () => {
    setLogEntries([]);
  };
  
  const filteredLogs = logEntries.filter(log => {
    const matchesLevel = logLevelFilter === 'all' || log.level === logLevelFilter;
    const matchesSearch = searchTerm === '' || 
      log.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (log.context && log.context.toLowerCase().includes(searchTerm.toLowerCase()));
    
    return matchesLevel && matchesSearch;
  });
  
  const getLogLevelColor = (level: string) => {
    switch (level) {
      case 'error': return 'bg-red-500';
      case 'warning': return 'bg-yellow-500';
      case 'info': return 'bg-blue-500';
      case 'debug': return 'bg-gray-500';
      default: return 'bg-green-500';
    }
  };
  
  return (
    <div className="flex flex-col h-full bg-gray-900 text-white">
      <div className="p-4 border-b border-gray-700">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <Terminal className="w-5 h-5" />
          Debugging Console
        </h2>
      </div>
      
      <div className="flex-1 overflow-hidden">
        <Tabs defaultValue="logs" className="h-full">
          <TabsList className="bg-gray-800 p-2">
            <TabsTrigger value="logs">Logs</TabsTrigger>
            <TabsTrigger value="traces">Execution Traces</TabsTrigger>
            <TabsTrigger value="breakpoints">Breakpoints</TabsTrigger>
            <TabsTrigger value="watches">Watch Expressions</TabsTrigger>
            <TabsTrigger value="events">Debug Events</TabsTrigger>
          </TabsList>
          
          <TabsContent value="logs" className="h-[calc(100%-40px)] p-4">
            <Card className="h-full bg-gray-800 border-gray-700">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Real-time Logs</CardTitle>
                <div className="flex items-center gap-2">
                  <Select value={logLevelFilter} onValueChange={setLogLevelFilter}>
                    <SelectTrigger className="w-[120px] bg-gray-700">
                      <SelectValue placeholder="Log Level" />
                    </SelectTrigger>
                    <SelectContent className="bg-gray-800">
                      <SelectItem value="all">All Levels</SelectItem>
                      <SelectItem value="error">Error</SelectItem>
                      <SelectItem value="warning">Warning</SelectItem>
                      <SelectItem value="info">Info</SelectItem>
                      <SelectItem value="debug">Debug</SelectItem>
                    </SelectContent>
                  </Select>
                  
                  <Input
                    placeholder="Search logs..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-[200px] bg-gray-700"
                  />
                  
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={clearLogs}
                    className="bg-gray-700 hover:bg-gray-600"
                  >
                    Clear
                  </Button>
                </div>
              </CardHeader>
              
              <CardContent className="h-[calc(100%-80px)]">
                <ScrollArea className="h-full pr-4">
                  <div className="space-y-2">
                    {filteredLogs.length === 0 ? (
                      <div className="text-gray-500 text-center py-4">
                        No logs available
                      </div>
                    ) : (
                      filteredLogs.map((log, index) => (
                        <div key={index} className="flex gap-2">
                          <Badge className={getLogLevelColor(log.level)}>
                            {log.level.toUpperCase()}
                          </Badge>
                          <div className="flex-1">
                            <div className="text-sm text-gray-400">
                              {new Date(log.timestamp).toLocaleTimeString()} - {log.context ? JSON.stringify(log.context) : ''}
                            </div>
                            <div className="text-sm">{log.message}</div>
                            {log.details && (
                              <div className="text-xs text-gray-500 mt-1">
                                {JSON.stringify(log.details)}
                              </div>
                            )}
                          </div>
                        </div>
                      ))
                    )}
                    <div ref={logEndRef} />
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="traces" className="h-[calc(100%-40px)] p-4">
            <Card className="h-full bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle>Execution Traces</CardTitle>
              </CardHeader>
              
              <CardContent className="h-[calc(100%-80px)]">
                <ScrollArea className="h-full">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Timestamp</TableHead>
                        <TableHead>Function</TableHead>
                        <TableHead>Duration</TableHead>
                        <TableHead>Status</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {executionTraces.length === 0 ? (
                        <TableRow>
                          <TableCell colSpan={4} className="text-center text-gray-500">
                            No execution traces available
                          </TableCell>
                        </TableRow>
                      ) : (
                        executionTraces.map((trace, index) => (
                          <TableRow key={index}>
                            <TableCell>{trace.timestamp ? new Date(trace.timestamp).toLocaleTimeString() : ''}</TableCell>
                            <TableCell>{trace.function_name}</TableCell>
                            <TableCell>{trace.duration_ms}ms</TableCell>
                            <TableCell>
                              <Badge className={trace.status === 'success' ? 'bg-green-500' : 'bg-red-500'}>
                                {trace.status}
                              </Badge>
                            </TableCell>
                          </TableRow>
                        ))
                      )}
                    </TableBody>
                  </Table>
                </ScrollArea>
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="breakpoints" className="h-[calc(100%-40px)] p-4">
            <Card className="h-full bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle>Breakpoints</CardTitle>
              </CardHeader>
              
              <CardContent className="h-[calc(100%-80px)]">
                <ScrollArea className="h-full">
                  {breakpoints.length === 0 ? (
                    <div className="text-gray-500 text-center py-4">
                      No breakpoints hit
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {breakpoints.map((bp, index) => (
                        <div key={index} className="p-3 border border-gray-700 rounded">
                          <div className="flex justify-between items-start">
                            <div>
                              <div className="font-semibold">
                                {bp.file}:{bp.line}
                              </div>
                              <div className="text-sm text-gray-400">
                                {bp.function_name}
                              </div>
                            </div>
                            <Badge className={bp.status === 'hit' ? 'bg-yellow-500' : 'bg-gray-500'}>
                              {bp.status}
                            </Badge>
                          </div>
                          <div className="mt-2 text-sm">
                            <div>Variables:</div>
                            <pre className="text-xs text-gray-400 mt-1 overflow-x-auto">
                              {JSON.stringify(bp.variables, null, 2)}
                            </pre>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </ScrollArea>
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="watches" className="h-[calc(100%-40px)] p-4">
            <Card className="h-full bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle>Watch Expressions</CardTitle>
                <div className="flex gap-2 mt-2">
                  <Input
                    placeholder="Add watch expression..."
                    value={watchExpressionInput}
                    onChange={(e) => setWatchExpressionInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && addWatchExpression()}
                    className="flex-1 bg-gray-700"
                  />
                  <Button
                    onClick={addWatchExpression}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    Add Watch
                  </Button>
                </div>
              </CardHeader>
              
              <CardContent className="h-[calc(100%-120px)]">
                <ScrollArea className="h-full">
                  {watchExpressions.length === 0 ? (
                    <div className="text-gray-500 text-center py-4">
                      No watch expressions added
                    </div>
                  ) : (
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Expression</TableHead>
                          <TableHead>Value</TableHead>
                          <TableHead>Type</TableHead>
                          <TableHead>Timestamp</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {watchExpressions.map((watch, index) => (
                          <TableRow key={index}>
                            <TableCell>{watch.expression}</TableCell>
                            <TableCell>{watch.value}</TableCell>
                            <TableCell>{watch.type}</TableCell>
                            <TableCell>{watch.timestamp ? new Date(watch.timestamp).toLocaleTimeString() : ''}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  )}
                </ScrollArea>
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="events" className="h-[calc(100%-40px)] p-4">
            <Card className="h-full bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle>Debug Events</CardTitle>
              </CardHeader>
              
              <CardContent className="h-[calc(100%-80px)]">
                <ScrollArea className="h-full">
                  {debugEvents.length === 0 ? (
                    <div className="text-gray-500 text-center py-4">
                      No debug events
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {debugEvents.map((event, index) => (
                        <div key={index} className="p-3 border border-gray-700 rounded">
                          <div className="flex justify-between items-start">
                            <div>
                              <div className="font-semibold">{event.event_type}</div>
                              <div className="text-sm text-gray-400">
                                {new Date(event.timestamp).toLocaleTimeString()}
                              </div>
                            </div>
                            <Badge className="bg-purple-500">{event.severity}</Badge>
                          </div>
                          <div className="mt-2 text-sm">
                            <div>{event.message}</div>
                            {event.data && (
                              <pre className="text-xs text-gray-400 mt-1 overflow-x-auto">
                                {JSON.stringify(event.data, null, 2)}
                              </pre>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </ScrollArea>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
      
      <div className="p-4 border-t border-gray-700 flex justify-between items-center">
        <div className="flex gap-2">
          <Button
            onClick={isDebugging ? stopDebugging : startDebugging}
            className={isDebugging ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'}
          >
            {isDebugging ? 'Stop Debugging' : 'Start Debugging'}
          </Button>
          
          <Button
            onClick={isMonitoring ? stopMonitoring : startMonitoring}
            className={isMonitoring ? 'bg-red-600 hover:bg-red-700' : 'bg-blue-600 hover:bg-blue-700'}
          >
            {isMonitoring ? 'Stop Monitoring' : 'Start Monitoring'}
          </Button>
        </div>
        
        <div className="flex gap-2">
          <Badge variant="outline" className="border-gray-600">
            {debugSocket.readyState === WebSocket.OPEN ? 'Connected' : 'Disconnected'}
          </Badge>
          <Badge variant="outline" className="border-gray-600">
            {logSocket.readyState === WebSocket.OPEN ? 'Logs Connected' : 'Logs Disconnected'}
          </Badge>
          <Badge variant="outline" className="border-gray-600">
            {performanceSocket.readyState === WebSocket.OPEN ? 'Monitoring Connected' : 'Monitoring Disconnected'}
          </Badge>
        </div>
      </div>
    </div>
  );
}