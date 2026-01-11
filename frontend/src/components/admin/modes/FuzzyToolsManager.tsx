import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../ui/card'
import { Button } from '../../ui/button'
import { Badge } from '../../ui/badge'
import { 
  Wrench, 
  Power, 
  PowerOff, 
  TestTube, 
  TrendingUp,
  Clock,
  CheckCircle2,
  XCircle,
  Loader2,
  Settings,
  BarChart3
} from 'lucide-react'
import {
  getFuzzyTools,
  enableFuzzyTool,
  disableFuzzyTool,
  testFuzzyTool
} from '../../../services/fuzzyService'
import type { FuzzyTool } from '../../../types/fuzzy'

export const FuzzyToolsManager = () => {
  const [tools, setTools] = useState<FuzzyTool[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedTool, setSelectedTool] = useState<FuzzyTool | null>(null)
  const [testingTool, setTestingTool] = useState<string | null>(null)
  const [togglingTool, setTogglingTool] = useState<string | null>(null)

  useEffect(() => {
    loadTools()
  }, [])

  const loadTools = async () => {
    try {
      setLoading(true)
      const toolsData = await getFuzzyTools()
      setTools(toolsData)
    } catch (err) {
      console.error('Error loading tools:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleToggleTool = async (tool: FuzzyTool) => {
    try {
      setTogglingTool(tool.id)
      
      const updatedTool = tool.enabled
        ? await disableFuzzyTool(tool.id)
        : await enableFuzzyTool(tool.id)

      setTools(prev => prev.map(t => t.id === tool.id ? updatedTool : t))
      
      if (selectedTool?.id === tool.id) {
        setSelectedTool(updatedTool)
      }
    } catch (err) {
      console.error('Error toggling tool:', err)
    } finally {
      setTogglingTool(null)
    }
  }

  const handleTestTool = async (tool: FuzzyTool) => {
    try {
      setTestingTool(tool.id)
      
      // Test with empty parameters - in a real implementation,
      // you'd want to provide appropriate test parameters
      const result = await testFuzzyTool(tool.id, {})
      
      alert(`Test Result:\n${result.success ? 'Success' : 'Failed'}\n${result.message}`)
    } catch (err) {
      alert(`Test Failed: ${err instanceof Error ? err.message : 'Unknown error'}`)
    } finally {
      setTestingTool(null)
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'enabled':
        return <Badge className="bg-green-500">Enabled</Badge>
      case 'disabled':
        return <Badge variant="secondary">Disabled</Badge>
      case 'maintenance':
        return <Badge variant="destructive">Maintenance</Badge>
      default:
        return <Badge variant="outline">{status}</Badge>
    }
  }

  const formatNumber = (num: number): string => {
    return new Intl.NumberFormat().format(num)
  }

  const formatDuration = (ms: number): string => {
    if (ms < 1000) return `${ms.toFixed(0)}ms`
    return `${(ms / 1000).toFixed(2)}s`
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
          <p className="text-muted-foreground">Loading FUZZY tools...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">FUZZY Tools Management</h2>
          <p className="text-muted-foreground mt-1">
            Manage and configure FUZZY's available tools
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={loadTools}>
          <Loader2 className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Tools Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Tools</CardTitle>
            <Wrench className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{tools.length}</div>
            <p className="text-xs text-muted-foreground">
              {tools.filter(t => t.enabled).length} enabled
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Usage</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatNumber(tools.reduce((sum, t) => sum + t.usage_count, 0))}
            </div>
            <p className="text-xs text-muted-foreground">
              All-time executions
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Success Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {(tools.reduce((sum, t) => sum + t.success_rate, 0) / tools.length).toFixed(1)}%
            </div>
            <p className="text-xs text-muted-foreground">
              Across all tools
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Tools List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {tools.map((tool) => (
          <Card 
            key={tool.id}
            className={`cursor-pointer transition-colors ${
              selectedTool?.id === tool.id ? 'border-primary' : ''
            }`}
            onClick={() => setSelectedTool(tool)}
          >
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <CardTitle className="text-lg">{tool.name}</CardTitle>
                    {getStatusBadge(tool.status)}
                  </div>
                  <CardDescription className="mt-2">
                    {tool.description}
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {/* Tool Stats */}
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div>
                  <p className="text-xs text-muted-foreground">Usage</p>
                  <p className="text-sm font-medium">{formatNumber(tool.usage_count)}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Success Rate</p>
                  <p className="text-sm font-medium">{tool.success_rate.toFixed(1)}%</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Avg Time</p>
                  <p className="text-sm font-medium">{formatDuration(tool.average_execution_time)}</p>
                </div>
              </div>

              {/* Tool Category */}
              <div className="mb-4">
                <Badge variant="outline">{tool.category}</Badge>
              </div>

              {/* Last Used */}
              {tool.last_used && (
                <p className="text-xs text-muted-foreground mb-4">
                  Last used: {new Date(tool.last_used).toLocaleString()}
                </p>
              )}

              {/* Actions */}
              <div className="flex gap-2">
                <Button
                  variant={tool.enabled ? 'destructive' : 'default'}
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation()
                    handleToggleTool(tool)
                  }}
                  disabled={togglingTool === tool.id}
                >
                  {togglingTool === tool.id ? (
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  ) : tool.enabled ? (
                    <PowerOff className="w-4 h-4 mr-2" />
                  ) : (
                    <Power className="w-4 h-4 mr-2" />
                  )}
                  {tool.enabled ? 'Disable' : 'Enable'}
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation()
                    handleTestTool(tool)
                  }}
                  disabled={testingTool === tool.id || !tool.enabled}
                >
                  {testingTool === tool.id ? (
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <TestTube className="w-4 h-4 mr-2" />
                  )}
                  Test
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Tool Details Panel */}
      {selectedTool && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Tool Details: {selectedTool.name}</CardTitle>
                <CardDescription>
                  Detailed information and configuration
                </CardDescription>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSelectedTool(null)}
              >
                Close
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Status and Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Status</p>
                <div className="mt-1">{getStatusBadge(selectedTool.status)}</div>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Enabled</p>
                <div className="mt-1">
                  {selectedTool.enabled ? (
                    <CheckCircle2 className="w-5 h-5 text-green-600" />
                  ) : (
                    <XCircle className="w-5 h-5 text-red-600" />
                  )}
                </div>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Category</p>
                <p className="text-sm font-medium mt-1">{selectedTool.category}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Tool ID</p>
                <p className="text-sm font-mono mt-1">{selectedTool.id}</p>
              </div>
            </div>

            {/* Description */}
            <div>
              <p className="text-sm font-medium mb-2">Description</p>
              <p className="text-sm text-muted-foreground">{selectedTool.description}</p>
            </div>

            {/* Performance Metrics */}
            <div>
              <p className="text-sm font-medium mb-2">Performance Metrics</p>
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-muted rounded-lg p-3">
                  <p className="text-xs text-muted-foreground">Total Usage</p>
                  <p className="text-lg font-bold">{formatNumber(selectedTool.usage_count)}</p>
                </div>
                <div className="bg-muted rounded-lg p-3">
                  <p className="text-xs text-muted-foreground">Success Rate</p>
                  <p className="text-lg font-bold">{selectedTool.success_rate.toFixed(1)}%</p>
                </div>
                <div className="bg-muted rounded-lg p-3">
                  <p className="text-xs text-muted-foreground">Avg Execution Time</p>
                  <p className="text-lg font-bold">{formatDuration(selectedTool.average_execution_time)}</p>
                </div>
              </div>
            </div>

            {/* Parameters */}
            {selectedTool.parameters && Object.keys(selectedTool.parameters).length > 0 && (
              <div>
                <p className="text-sm font-medium mb-2">Parameters</p>
                <pre className="bg-muted rounded-lg p-3 text-xs overflow-x-auto">
                  {JSON.stringify(selectedTool.parameters, null, 2)}
                </pre>
              </div>
            )}

            {/* Last Used */}
            {selectedTool.last_used && (
              <div>
                <p className="text-sm font-medium mb-2">Last Used</p>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Clock className="w-4 h-4" />
                  {new Date(selectedTool.last_used).toLocaleString()}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
