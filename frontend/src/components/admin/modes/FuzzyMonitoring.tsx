import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../ui/card'
import { Button } from '../../ui/button'
import { 
  Activity, 
  TrendingUp, 
  Users, 
  Zap, 
  Clock, 
  AlertTriangle,
  RefreshCw,
  Loader2,
  CheckCircle2,
  XCircle
} from 'lucide-react'
import {
  getFuzzyStatistics,
  getFuzzyPerformance,
  getFuzzyActions,
  getFuzzyActivityLogs
} from '../../../services/fuzzyService'
import type {
  FuzzyUsageStatistics,
  FuzzyPerformanceMetrics,
  FuzzyAction,
  FuzzyActivityLog
} from '../../../types/fuzzy'

export const FuzzyMonitoring = () => {
  const [statistics, setStatistics] = useState<FuzzyUsageStatistics | null>(null)
  const [performance, setPerformance] = useState<FuzzyPerformanceMetrics | null>(null)
  const [recentActions, setRecentActions] = useState<FuzzyAction[]>([])
  const [activityLogs, setActivityLogs] = useState<FuzzyActivityLog[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [autoRefresh, setAutoRefresh] = useState(true)

  useEffect(() => {
    loadMonitoringData()
  }, [])

  useEffect(() => {
    if (!autoRefresh) return

    const interval = setInterval(() => {
      loadMonitoringData(true)
    }, 30000) // Refresh every 30 seconds

    return () => clearInterval(interval)
  }, [autoRefresh])

  const loadMonitoringData = async (isRefresh = false) => {
    try {
      if (isRefresh) {
        setRefreshing(true)
      } else {
        setLoading(true)
      }

      const [statsData, perfData, actionsData, logsData] = await Promise.all([
        getFuzzyStatistics(),
        getFuzzyPerformance(),
        getFuzzyActions(undefined, undefined, undefined, 10, 0),
        getFuzzyActivityLogs(undefined, 20, 0)
      ])

      setStatistics(statsData)
      setPerformance(perfData)
      setRecentActions(actionsData.actions)
      setActivityLogs(logsData.logs)
    } catch (err) {
      console.error('Error loading monitoring data:', err)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const formatNumber = (num: number): string => {
    return new Intl.NumberFormat().format(num)
  }

  const formatDuration = (ms: number): string => {
    if (ms < 1000) return `${ms.toFixed(0)}ms`
    return `${(ms / 1000).toFixed(2)}s`
  }

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'completed':
        return 'text-green-600 dark:text-green-400'
      case 'failed':
        return 'text-red-600 dark:text-red-400'
      case 'executing':
        return 'text-blue-600 dark:text-blue-400'
      default:
        return 'text-gray-600 dark:text-gray-400'
    }
  }

  const getLogLevelColor = (level: string): string => {
    switch (level) {
      case 'error':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
      case 'info':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
          <p className="text-muted-foreground">Loading monitoring data...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">FUZZY Monitoring Dashboard</h2>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setAutoRefresh(!autoRefresh)}
          >
            {autoRefresh ? 'Disable' : 'Enable'} Auto-Refresh
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => loadMonitoringData(true)}
            disabled={refreshing}
          >
            {refreshing ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <RefreshCw className="w-4 h-4 mr-2" />
            )}
            Refresh
          </Button>
        </div>
      </div>

      {/* Statistics Cards */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Sessions</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatNumber(statistics.total_sessions)}</div>
              <p className="text-xs text-muted-foreground">
                {statistics.active_sessions} active
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Actions</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatNumber(statistics.total_actions)}</div>
              <p className="text-xs text-muted-foreground">
                {statistics.actions_per_hour.toFixed(1)}/hour
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {((statistics.successful_actions / statistics.total_actions) * 100).toFixed(1)}%
              </div>
              <p className="text-xs text-muted-foreground">
                {formatNumber(statistics.successful_actions)} successful
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Response Time</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatDuration(statistics.average_response_time)}
              </div>
              <p className="text-xs text-muted-foreground">
                {statistics.unique_users} unique users
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Performance Metrics */}
      {performance && (
        <Card>
          <CardHeader>
            <CardTitle>Performance Metrics</CardTitle>
            <CardDescription>Real-time performance indicators</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Uptime</p>
                <p className="text-2xl font-bold">{performance.uptime_percentage.toFixed(2)}%</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Error Rate</p>
                <p className="text-2xl font-bold">{performance.error_rate.toFixed(2)}%</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">P95 Response</p>
                <p className="text-2xl font-bold">{formatDuration(performance.p95_response_time)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Requests/min</p>
                <p className="text-2xl font-bold">{performance.requests_per_minute.toFixed(1)}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Most Used Tools */}
      {statistics && statistics.most_used_tools.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Most Used Tools</CardTitle>
            <CardDescription>Top tools by usage count</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {statistics.most_used_tools.map((tool, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Zap className="w-4 h-4 text-primary" />
                    <span className="font-medium">{tool.tool_name}</span>
                  </div>
                  <span className="text-muted-foreground">{formatNumber(tool.usage_count)} uses</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recent Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Actions</CardTitle>
          <CardDescription>Latest FUZZY actions and their status</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {recentActions.length === 0 ? (
              <p className="text-center text-muted-foreground py-4">No recent actions</p>
            ) : (
              recentActions.map((action) => (
                <div key={action.id} className="flex items-start justify-between border-b pb-3 last:border-0">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      {action.status === 'completed' ? (
                        <CheckCircle2 className="w-4 h-4 text-green-600" />
                      ) : action.status === 'failed' ? (
                        <XCircle className="w-4 h-4 text-red-600" />
                      ) : (
                        <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                      )}
                      <span className="font-medium">{action.action_name}</span>
                    </div>
                    {action.description && (
                      <p className="text-sm text-muted-foreground mt-1 ml-6">
                        {action.description}
                      </p>
                    )}
                    <div className="flex items-center gap-4 mt-2 ml-6 text-xs text-muted-foreground">
                      <span>{new Date(action.created_at).toLocaleString()}</span>
                      {action.execution_time_ms && (
                        <span>{formatDuration(action.execution_time_ms)}</span>
                      )}
                    </div>
                  </div>
                  <span className={`text-sm font-medium ${getStatusColor(action.status)}`}>
                    {action.status}
                  </span>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>

      {/* Activity Logs */}
      <Card>
        <CardHeader>
          <CardTitle>Activity Logs</CardTitle>
          <CardDescription>System activity and events</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {activityLogs.length === 0 ? (
              <p className="text-center text-muted-foreground py-4">No activity logs</p>
            ) : (
              activityLogs.map((log) => (
                <div key={log.id} className="flex items-start gap-3 text-sm">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${getLogLevelColor(log.level)}`}>
                    {log.level.toUpperCase()}
                  </span>
                  <div className="flex-1">
                    <p>{log.message}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {new Date(log.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
