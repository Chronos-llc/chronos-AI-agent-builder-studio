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
  Loader2,
  BookOpen,
  PlusCircle,
  List
} from 'lucide-react'
import { SkillsLibrary } from './SkillsLibrary'
import { SkillCreator } from './SkillCreator'
import { getSkillsStatistics } from '../../../services/skillsService'
import type { SkillStatistics } from '../../../types/skills'

type TabValue = 'library' | 'creator' | 'statistics'

export const SkillsMode = () => {
  const [activeTab, setActiveTab] = useState<TabValue>('library')
  const [statistics, setStatistics] = useState<SkillStatistics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadStatistics()
  }, [])

  const loadStatistics = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const stats = await getSkillsStatistics()
      setStatistics(stats)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load skills statistics')
      console.error('Error loading skills statistics:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
          <p className="text-muted-foreground">Loading Skills Management...</p>
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
            onClick={loadStatistics}
            className="ml-4 underline hover:no-underline"
          >
            Retry
          </button>
        </AlertDescription>
      </Alert>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Skills Management</h1>
          <p className="text-muted-foreground mt-1">
            Create, manage, and organize skills for AI agents
          </p>
        </div>
        
        {/* Statistics Badges */}
        {statistics && (
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
              <BookOpen className="w-4 h-4" />
              <span className="font-medium">{statistics.total_skills} Skills</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
              <PlusCircle className="w-4 h-4" />
              <span className="font-medium">{statistics.active_skills} Active</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
              <List className="w-4 h-4" />
              <span className="font-medium">{statistics.total_installations} Installs</span>
            </div>
          </div>
        )}
      </div>

      {/* Main Content Tabs */}
      <Card className="p-6">
        <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as TabValue)}>
          <TabsList className="grid w-full grid-cols-3 mb-6">
            <TabsTrigger value="library" className="flex items-center gap-2">
              <BookOpen className="w-4 h-4" />
              Skills Library
            </TabsTrigger>
            <TabsTrigger value="creator" className="flex items-center gap-2">
              <PlusCircle className="w-4 h-4" />
              Create Skill
            </TabsTrigger>
            <TabsTrigger value="statistics" className="flex items-center gap-2">
              <Activity className="w-4 h-4" />
              Statistics
            </TabsTrigger>
          </TabsList>

          <TabsContent value="library" className="space-y-4">
            <SkillsLibrary />
          </TabsContent>

          <TabsContent value="creator" className="space-y-4">
            <SkillCreator />
          </TabsContent>

          <TabsContent value="statistics" className="space-y-4">
            {statistics && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* Total Skills Card */}
                <Card className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold">Total Skills</h3>
                      <p className="text-3xl font-bold mt-2">{statistics.total_skills}</p>
                    </div>
                    <BookOpen className="w-8 h-8 text-blue-500" />
                  </div>
                </Card>

                {/* Active Skills Card */}
                <Card className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold">Active Skills</h3>
                      <p className="text-3xl font-bold mt-2">{statistics.active_skills}</p>
                    </div>
                    <PlusCircle className="w-8 h-8 text-green-500" />
                  </div>
                </Card>

                {/* Total Installations Card */}
                <Card className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold">Total Installations</h3>
                      <p className="text-3xl font-bold mt-2">{statistics.total_installations}</p>
                    </div>
                    <List className="w-8 h-8 text-purple-500" />
                  </div>
                </Card>

                {/* Popular Categories */}
                <Card className="p-6 md:col-span-2">
                  <h3 className="text-lg font-semibold mb-4">Popular Categories</h3>
                  <div className="space-y-3">
                    {statistics.popular_categories.map((category, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-secondary rounded-lg">
                        <div className="flex items-center gap-3">
                          <span className="font-medium">{category.category}</span>
                        </div>
                        <div className="flex items-center gap-4">
                          <span className="text-muted-foreground">{category.count} skills</span>
                          <div className="w-24 h-2 bg-primary rounded-full">
                            <div 
                              className="h-full bg-primary-foreground rounded-full"
                              style={{ width: `${(category.count / statistics.total_skills) * 100}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>

                {/* Recent Skills */}
                <Card className="p-6">
                  <h3 className="text-lg font-semibold mb-4">Recent Skills</h3>
                  <div className="space-y-4">
                    {statistics.recent_skills.map((skill) => (
                      <div key={skill.id} className="flex items-center gap-3 p-3 bg-secondary rounded-lg">
                        <div className="w-8 h-8 bg-blue-500 text-white rounded flex items-center justify-center font-bold">
                          {skill.icon?.charAt(0) || 'S'}
                        </div>
                        <div className="flex-1">
                          <div className="font-medium">{skill.display_name}</div>
                          <div className="text-sm text-muted-foreground">{skill.category}</div>
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {skill.install_count} installs
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </Card>
    </div>
  )
}