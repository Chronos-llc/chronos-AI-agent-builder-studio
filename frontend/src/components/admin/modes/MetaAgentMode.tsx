import { useState, useEffect } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../ui/tabs'
import { Card } from '../../ui/card'
import { Alert, AlertDescription } from '../../ui/alert'
import { 
  Settings, 
  Activity, 
  TestTube, 
  Wrench, 
  AlertCircle,
  Loader2 
} from 'lucide-react'
import { FuzzyConfiguration } from './FuzzyConfiguration'
import { FuzzyMonitoring } from './FuzzyMonitoring'
import { FuzzyTesting } from './FuzzyTesting'
import { FuzzyToolsManager } from './FuzzyToolsManager'
import { getFuzzyConfiguration, getFuzzyHealth } from '../../../services/fuzzyService'
import type { FuzzyConfiguration as FuzzyConfigType, FuzzyHealthStatus } from '../../../types/fuzzy'

type TabValue = 'configuration' | 'monitoring' | 'testing' | 'tools'

export const MetaAgentMode = () => {
  const [activeTab, setActiveTab] = useState<TabValue>('configuration')
  const [configuration, setConfiguration] = useState<FuzzyConfigType | null>(null)
  const [health, setHealth] = useState<FuzzyHealthStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [serviceUnavailable, setServiceUnavailable] = useState(false)

  useEffect(() => {
    loadInitialData()
  }, [])

  const loadInitialData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const [configData, healthData] = await Promise.all([
        getFuzzyConfiguration(),
        getFuzzyHealth()
      ])
      
      setConfiguration(configData)
      setHealth(healthData)
      setServiceUnavailable(false)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load FUZZY data'
      const likelyUnavailable =
        message.toLowerCase().includes('404') ||
        message.toLowerCase().includes('not found') ||
        message.toLowerCase().includes('failed to fetch')
      if (likelyUnavailable) {
        setServiceUnavailable(true)
        setError(null)
      } else {
        setError(message)
      }
      console.error('Error loading FUZZY data:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleConfigurationUpdate = (updatedConfig: FuzzyConfigType) => {
    setConfiguration(updatedConfig)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
          <p className="text-muted-foreground">Loading FUZZY configuration...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          {error}
          <button 
            onClick={loadInitialData}
            className="ml-4 underline hover:no-underline"
          >
            Retry
          </button>
        </AlertDescription>
      </Alert>
    )
  }

  if (serviceUnavailable) {
    return (
      <div className="space-y-4">
        <Alert variant="warning">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            FUZZY admin endpoints are not available in this environment yet. Other admin modes remain fully usable.
            <button
              onClick={loadInitialData}
              className="ml-4 underline hover:no-underline"
            >
              Retry
            </button>
          </AlertDescription>
        </Alert>
        <Card className="p-6">
          <h3 className="text-lg font-semibold">FUZZY Meta-Agent (Partial Availability)</h3>
          <p className="mt-2 text-sm text-muted-foreground">
            Configure FUZZY endpoints and enable the corresponding backend surface, then retry this panel.
          </p>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">FUZZY Meta-Agent Management</h1>
          <p className="text-muted-foreground mt-1">
            Configure and monitor the FUZZY meta-agent for studio automation
          </p>
        </div>
        
        {/* Health Status Badge */}
        {health && (
          <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
            health.status === 'healthy' 
              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
              : health.status === 'degraded'
              ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
              : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
          }`}>
            <div className={`w-2 h-2 rounded-full ${
              health.status === 'healthy' ? 'bg-green-500' :
              health.status === 'degraded' ? 'bg-yellow-500' : 'bg-red-500'
            }`} />
            <span className="font-medium capitalize">{health.status}</span>
          </div>
        )}
      </div>

      {/* Health Issues Alert */}
      {health && health.issues.length > 0 && (
        <Alert variant="warning">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            <strong>Health Issues Detected:</strong>
            <ul className="mt-2 ml-4 list-disc">
              {health.issues.map((issue, index) => (
                <li key={index}>{issue}</li>
              ))}
            </ul>
          </AlertDescription>
        </Alert>
      )}

      {/* Main Content Tabs */}
      <Card className="p-6">
        <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as TabValue)}>
          <TabsList className="grid w-full grid-cols-4 mb-6">
            <TabsTrigger value="configuration" className="flex items-center gap-2">
              <Settings className="w-4 h-4" />
              Configuration
            </TabsTrigger>
            <TabsTrigger value="monitoring" className="flex items-center gap-2">
              <Activity className="w-4 h-4" />
              Monitoring
            </TabsTrigger>
            <TabsTrigger value="testing" className="flex items-center gap-2">
              <TestTube className="w-4 h-4" />
              Testing
            </TabsTrigger>
            <TabsTrigger value="tools" className="flex items-center gap-2">
              <Wrench className="w-4 h-4" />
              Tools
            </TabsTrigger>
          </TabsList>

          <TabsContent value="configuration" className="space-y-4">
            {configuration && (
              <FuzzyConfiguration
                configuration={configuration}
                onUpdate={handleConfigurationUpdate}
              />
            )}
          </TabsContent>

          <TabsContent value="monitoring" className="space-y-4">
            <FuzzyMonitoring />
          </TabsContent>

          <TabsContent value="testing" className="space-y-4">
            <FuzzyTesting />
          </TabsContent>

          <TabsContent value="tools" className="space-y-4">
            <FuzzyToolsManager />
          </TabsContent>
        </Tabs>
      </Card>
    </div>
  )
}
