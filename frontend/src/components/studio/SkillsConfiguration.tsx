import { useState, useEffect } from 'react'
import { Card } from '../ui/card'
import { Button } from '../ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs'
import { Alert, AlertDescription } from '../ui/alert'
import { 
  PlusCircle, 
  List, 
  AlertCircle,
  Loader2,
  CheckCircle2,
  XCircle,
  Edit,
  RefreshCw
} from 'lucide-react'
import { SkillSelector } from './SkillSelector'
import { Badge } from '../ui/badge'
import { 
  getAgentSkills, 
  uninstallSkillFromAgent,
  updateAgentSkillInstallation
} from '../../services/skillsService'
import type { AgentSkillInstallation } from '../../types/skills'

export const SkillsConfiguration = () => {
  const [agentId] = useState<number>(1) // This would come from props or context
  const [installedSkills, setInstalledSkills] = useState<AgentSkillInstallation[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'installed' | 'add'>('installed')

  useEffect(() => {
    loadInstalledSkills()
  }, [agentId])

  const loadInstalledSkills = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const result = await getAgentSkills(agentId)
      setInstalledSkills(result.items)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load installed skills')
      console.error('Error loading installed skills:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleUninstallSkill = async (installationId: number) => {
    if (!window.confirm('Are you sure you want to uninstall this skill?')) {
      return
    }
    
    try {
      await uninstallSkillFromAgent(agentId, installationId)
      await loadInstalledSkills()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to uninstall skill')
      console.error('Error uninstalling skill:', err)
    }
  }

  const handleToggleSkill = async (installationId: number, isEnabled: boolean) => {
    try {
      await updateAgentSkillInstallation(agentId, installationId, {
        is_enabled: !isEnabled
      })
      await loadInstalledSkills()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update skill')
      console.error('Error updating skill:', err)
    }
  }

  const handleSkillsAdded = () => {
    // This would be called when skills are added from SkillSelector
    // For now, just refresh the list
    loadInstalledSkills()
    setActiveTab('installed')
  }

  const getCategoryIcon = (category?: string) => {
    if (!category) return '📚'
    
    const icons: Record<string, string> = {
      'analysis': '📊',
      'automation': '⚙️',
      'communication': '💬',
      'integration': '🔗',
      'data': '🗃️',
      'ai': '🤖',
      'utility': '🔧'
    }
    
    return icons[category.toLowerCase()] || '📚'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Agent Skills Configuration</h2>
          <p className="text-muted-foreground mt-1">
            Manage skills for your AI agent
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <Button 
            variant="outline"
            onClick={() => setActiveTab('add')}
            className="gap-2"
          >
            <PlusCircle className="w-4 h-4" />
            Add Skills
          </Button>
          <Button 
            variant="outline"
            onClick={loadInstalledSkills}
            disabled={loading}
            className="gap-2"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <RefreshCw className="w-4 h-4" />
            )}
            Refresh
          </Button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Main Content */}
      <Card className="p-6">
        <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as 'installed' | 'add')}>
          <TabsList className="grid w-full grid-cols-2 mb-6">
            <TabsTrigger value="installed" className="flex items-center gap-2">
              <List className="w-4 h-4" />
              Installed Skills
            </TabsTrigger>
            <TabsTrigger value="add" className="flex items-center gap-2">
              <PlusCircle className="w-4 h-4" />
              Add Skills
            </TabsTrigger>
          </TabsList>

          <TabsContent value="installed" className="space-y-4">
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
              </div>
            ) : (
              <div className="space-y-6">
                {installedSkills.length === 0 ? (
                  <div className="text-center py-12">
                    <p className="text-muted-foreground mb-4">No skills installed yet</p>
                    <Button 
                      variant="outline"
                      onClick={() => setActiveTab('add')}
                      className="gap-2"
                    >
                      <PlusCircle className="w-4 h-4" />
                      Add Skills
                    </Button>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {installedSkills.map((installation) => (
                      <Card key={installation.id} className="p-4">
                        <div className="space-y-4">
                          {/* Header */}
                          <div className="flex items-start justify-between">
                            <div className="flex items-center gap-3">
                              <div className="w-10 h-10 bg-primary text-primary-foreground rounded-lg flex items-center justify-center font-bold text-lg">
                                {getCategoryIcon(installation.skill?.category)}
                              </div>
                              <div>
                                <h3 className="font-semibold">{installation.skill?.display_name}</h3>
                                <p className="text-sm text-muted-foreground">{installation.skill?.name}</p>
                              </div>
                            </div>
                            
                            <div className="flex items-center gap-2">
                              {installation.skill?.is_premium && (
                                <Badge variant="secondary" className="gap-1">
                                  Premium
                                </Badge>
                              )}
                              <Badge variant={installation.is_enabled ? 'default' : 'secondary'}>
                                {installation.is_enabled ? 'Enabled' : 'Disabled'}
                              </Badge>
                            </div>
                          </div>
                          
                          {/* Description */}
                          <div className="text-sm text-muted-foreground">
                            <p className="line-clamp-3">{installation.skill?.description || 'No description provided'}</p>
                          </div>
                          
                          {/* Metadata */}
                          <div className="flex flex-wrap gap-2 text-xs">
                            {installation.skill?.category && (
                              <Badge variant="outline" className="gap-1">
                                {installation.skill.category}
                              </Badge>
                            )}
                            {installation.skill?.version && (
                              <Badge variant="outline" className="gap-1">
                                v{installation.skill.version}
                              </Badge>
                            )}
                            <Badge variant="outline" className="gap-1">
                              Installed: {new Date(installation.installed_at).toLocaleDateString()}
                            </Badge>
                          </div>
                          
                          {/* Actions */}
                          <div className="flex items-center gap-2 pt-2 border-t">
                            <Button 
                              variant="outline" 
                              size="sm" 
                              className="flex-1 gap-1"
                              onClick={() => handleToggleSkill(installation.id, installation.is_enabled)}
                            >
                              {installation.is_enabled ? (
                                <XCircle className="w-3 h-3 text-red-500" />
                              ) : (
                                <CheckCircle2 className="w-3 h-3 text-green-500" />
                              )}
                              {installation.is_enabled ? 'Disable' : 'Enable'}
                            </Button>
                            <Button 
                              variant="outline" 
                              size="sm" 
                              className="flex-1 gap-1"
                            >
                              <Edit className="w-3 h-3" />
                              Configure
                            </Button>
                            <Button 
                              variant="destructive" 
                              size="sm" 
                              className="flex-1 gap-1"
                              onClick={() => handleUninstallSkill(installation.id)}
                            >
                              Uninstall
                            </Button>
                          </div>
                        </div>
                      </Card>
                    ))}
                  </div>
                )}
              </div>
            )}
          </TabsContent>

          <TabsContent value="add" className="space-y-4">
            <SkillSelector onSkillsAdded={handleSkillsAdded} />
          </TabsContent>
        </Tabs>
      </Card>
    </div>
  )
}