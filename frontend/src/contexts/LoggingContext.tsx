import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { LogEntry, LogLevel, LogSource } from '../types/logging';

interface LoggingContextType {
  logs: LogEntry[];
  addLog: (log: LogEntry) => void;
  clearLogs: () => void;
  exportLogs: () => string;
  filterLogs: (level?: LogLevel, source?: LogSource) => LogEntry[];
  setFilter: (level?: LogLevel, source?: LogSource) => void;
  searchLogs: (searchTerm: string) => LogEntry[];
  setSearchTerm: (searchTerm: string) => void;
  getFilteredLogs: () => LogEntry[];
  getLogStatistics: () => {
    total: number;
    byLevel: Record<LogLevel, number>;
    bySource: Record<LogSource, number>;
  };
  downloadLogs: () => void;
  importLogs: (logs: LogEntry[]) => void;
}

export const LoggingContext = createContext<LoggingContextType | undefined>(undefined);

export const LoggingProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [filter, setFilter] = useState<{ level?: LogLevel; source?: LogSource }>({});
  const [searchTerm, setSearchTerm] = useState<string>('');

  const addLog = useCallback((log: LogEntry) => {
    setLogs(prevLogs => [...prevLogs, log]);
  }, []);

  const clearLogs = useCallback(() => {
    setLogs([]);
  }, []);

  const exportLogs = useCallback(() => {
    return JSON.stringify(logs, null, 2);
  }, [logs]);

  const filterLogs = useCallback((level?: LogLevel, source?: LogSource) => {
    return logs.filter(log => 
      (!level || log.level === level) && 
      (!source || log.source === source)
    );
  }, [logs]);

  const searchLogs = useCallback((searchTerm: string) => {
    return logs.filter(log => 
      log.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.source.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [logs]);

  const getFilteredLogs = useCallback(() => {
    let filtered = logs;
    
    if (filter.level) {
      filtered = filtered.filter(log => log.level === filter.level);
    }
    
    if (filter.source) {
      filtered = filtered.filter(log => log.source === filter.source);
    }
    
    if (searchTerm) {
      filtered = filtered.filter(log => 
        log.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
        log.source.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    return filtered;
  }, [logs, filter, searchTerm]);

  const getLogStatistics = useCallback(() => {
    const byLevel: Record<LogLevel, number> = {
      debug: 0,
      info: 0,
      warn: 0,
      error: 0
    };
    
    const bySource: Record<LogSource, number> = {
      system: 0,
      action: 0,
      hook: 0,
      agent: 0,
      user: 0
    };
    
    logs.forEach(log => {
      byLevel[log.level] = (byLevel[log.level] || 0) + 1;
      bySource[log.source] = (bySource[log.source] || 0) + 1;
    });
    
    return {
      total: logs.length,
      byLevel,
      bySource
    };
  }, [logs]);

  const downloadLogs = useCallback(() => {
    const data = exportLogs();
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `logs-${new Date().toISOString()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }, [exportLogs]);

  const importLogs = useCallback((importedLogs: LogEntry[]) => {
    setLogs(prevLogs => [...prevLogs, ...importedLogs]);
  }, []);

  const value: LoggingContextType = {
    logs,
    addLog,
    clearLogs,
    exportLogs,
    filterLogs,
    setFilter,
    searchLogs,
    setSearchTerm,
    getFilteredLogs,
    getLogStatistics,
    downloadLogs,
    importLogs
  };

  return (
    <LoggingContext.Provider value={value}>
      {children}
    </LoggingContext.Provider>
  );
};

export const useLogging = () => {
  const context = useContext(LoggingContext);
  if (!context) {
    throw new Error('useLogging must be used within a LoggingProvider');
  }
  return context;
};