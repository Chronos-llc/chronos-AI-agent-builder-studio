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
  List,
  Megaphone,
  Eye,
  Calendar,
  Users,
  BarChart2,
  Edit,
  Trash2,
  CheckCircle,
  XCircle,
  Clock
} from 'lucide-react'
import { Button } from '../../ui/button'
import { Input } from '../../ui/input'
import { Textarea } from '../../ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../ui/select'
import { Switch } from '../../ui/switch'
import { Badge } from '../../ui/badge'
import { useToast } from '../../ui/use-toast'
import type { PlatformUpdate, UpdateType, UpdatePriority, TargetAudience } from '../../../types/platformUpdates'

// Mock data and functions - these would be replaced with actual API calls
type TabValue = 'updates' | 'create' | 'statistics'

export const PlatformUpdatesMode = () => {
  const [activeTab, setActiveTab] = useState<TabValue>('updates')
  const [updates, setUpdates] = useState<PlatformUpdate[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [stats, setStats] = useState<any>(null)
  const { toast } = useToast()

  // Form state for creating/editing updates
  const [formData, setFormData] = useState({
    id: null as number | null,
    title: '',
    description: '',
    update_type: 'ANNOUNCEMENT' as UpdateType,
    priority: 'NORMAL' as UpdatePriority,
    media_type: 'NONE' as 'IMAGE' | 'VIDEO' | 'NONE',
    media_urls: [] as string[],
    thumbnail_url: '',
    target_audience: 'ALL' as TargetAudience,
    is_published: false,
    published_at: null as string | null,
    expires_at: null as string | null
  })

  const [mediaUrlInput, setMediaUrlInput] = useState('')

  useEffect(() => {
    loadUpdates()
    loadStatistics()
  }, [])

  const loadUpdates = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Mock API call - replace with actual API
      const mockUpdates: PlatformUpdate[] = [
        {
          id: 1,
          title: "New AI Features Released",
          description: "We've added powerful new AI capabilities including advanced natural language processing and improved workflow automation.",
          update_type: 'FEATURE',
          priority: 'HIGH',
          media_type: 'IMAGE',
          media_urls: ['https://example.com/image1.jpg'],
          thumbnail_url: 'https://example.com/thumb1.jpg',
          target_audience: 'ALL',
          is_published: true,
          view_count: 42,
          published_at: '2026-01-10T10:00:00Z',
          expires_at: null,
          created_at: '2026-01-09T14:30:00Z',
          updated_at: '2026-01-10T09:45:00Z'
        },
        {
          id: 2,
          title: "Scheduled Maintenance",
          description: "The platform will undergo maintenance on January 15th from 2-4 AM UTC. Expect brief downtime.",
          update_type: 'MAINTENANCE',
          priority: 'NORMAL',
          media_type: 'NONE',
          media_urls: [],
          thumbnail_url: '',
          target_audience: 'ALL',
          is_published: true,
          view_count: 28,
          published_at: '2026-01-08T08:00:00Z',
          expires_at: '2026-01-16T00:00:00Z',
          created_at: '2026-01-07T11:15:00Z',
          updated_at: '2026-01-08T07:50:00Z'
        }
      ]
      
      setUpdates(mockUpdates)
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load platform updates')
      console.error('Error loading platform updates:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadStatistics = async () => {
    try {
      // Mock statistics
      const mockStats = {
        total_updates: 12,
        published_updates: 8,
        draft_updates: 4,
        total_views: 428,
        by_type: {
          FEATURE: 4,
          BUG_FIX: 2,
          ANNOUNCEMENT: 3,
          MAINTENANCE: 2,
          SECURITY: 1
        },
        by_priority: {
          LOW: 2,
          NORMAL: 6,
          HIGH: 3,
          CRITICAL: 1
        }
      }
      
      setStats(mockStats)
      
    } catch (err) {
      console.error('Error loading statistics:', err)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSelectChange = (name: string, value: string) => {
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSwitchChange = (name: string, checked: boolean) => {
    setFormData(prev => ({ ...prev, [name]: checked }))
  }

  const addMediaUrl = () => {
    if (mediaUrlInput.trim()) {
      setFormData(prev => ({
        ...prev,
        media_urls: [...prev.media_urls, mediaUrlInput.trim()]
      }))
      setMediaUrlInput('')
    }
  }

  const removeMediaUrl = (index: number) => {
    setFormData(prev => ({
      ...prev,
      media_urls: prev.media_urls.filter((_, i) => i !== index)
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      setLoading(true)
      
      // Mock API call
      if (formData.id) {
        // Update existing
        toast({
          title: "Update Updated",
          description: "Platform update has been successfully updated.",
          variant: "success"
        })
      } else {
        // Create new
        const newUpdate: PlatformUpdate = {
          id: updates.length + 1,
          title: formData.title,
          description: formData.description,
          update_type: formData.update_type,
          priority: formData.priority,
          media_type: formData.media_type,
          media_urls: formData.media_urls,
          thumbnail_url: formData.thumbnail_url,
          target_audience: formData.target_audience,
          is_published: formData.is_published,
          view_count: 0,
          published_at: formData.is_published ? new Date().toISOString() : null,
          expires_at: formData.expires_at,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
        
        setUpdates([...updates, newUpdate])
        
        toast({
          title: "Update Created",
          description: "New platform update has been successfully created.",
          variant: "success"
        })
        
        // Reset form
        setFormData({
          id: null,
          title: '',
          description: '',
          update_type: 'ANNOUNCEMENT',
          priority: 'NORMAL',
          media_type: 'NONE',
          media_urls: [],
          thumbnail_url: '',
          target_audience: 'ALL',
          is_published: false,
          published_at: null,
          expires_at: null
        })
      }
      
      setActiveTab('updates')
      
    } catch (err) {
      toast({
        title: "Error",
        description: err instanceof Error ? err.message : 'Failed to save update',
        variant: "destructive"
      })
      console.error('Error saving update:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleEdit = (update: PlatformUpdate) => {
    setFormData({
      id: update.id,
      title: update.title,
      description: update.description,
      update_type: update.update_type,
      priority: update.priority,
      media_type: update.media_type as 'IMAGE' | 'VIDEO' | 'NONE',
      media_urls: update.media_urls,
      thumbnail_url: update.thumbnail_url,
      target_audience: update.target_audience,
      is_published: update.is_published,
      published_at: update.published_at,
      expires_at: update.expires_at
    })
    setActiveTab('create')
  }

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this update?')) {
      try {
        setLoading(true)
        // Mock API call
        setUpdates(updates.filter(update => update.id !== id))
        
        toast({
          title: "Update Deleted",
          description: "Platform update has been successfully deleted.",
          variant: "success"
        })
        
      } catch (err) {
        toast({
          title: "Error",
          description: err instanceof Error ? err.message : 'Failed to delete update',
          variant: "destructive"
        })
        console.error('Error deleting update:', err)
      } finally {
        setLoading(false)
      }
    }
  }

  const handlePublishToggle = async (id: number, currentStatus: boolean) => {
    try {
      setLoading(true)
      // Mock API call
      setUpdates(updates.map(update => 
        update.id === id ? {
          ...update,
          is_published: !currentStatus,
          published_at: !currentStatus ? new Date().toISOString() : null
        } : update
      ))
      
      toast({
        title: "Update Status Changed",
        description: `Update has been ${!currentStatus ? 'published' : 'unpublished'}.`,
        variant: "success"
      })
      
    } catch (err) {
      toast({
        title: "Error",
        description: err instanceof Error ? err.message : 'Failed to change update status',
        variant: "destructive"
      })
      console.error('Error changing update status:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
          <p className="text-muted-foreground">Loading Platform Updates...</p>
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
            onClick={loadUpdates}
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
          <h1 className="text-3xl font-bold">Platform Updates Management</h1>
          <p className="text-muted-foreground mt-1">
            Create, manage, and publish platform-wide announcements and updates
          </p>
        </div>
        
        {/* Statistics Badges */}
        {stats && (
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
              <Megaphone className="w-4 h-4" />
              <span className="font-medium">{stats.total_updates} Updates</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
              <CheckCircle className="w-4 h-4" />
              <span className="font-medium">{stats.published_updates} Published</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
              <Eye className="w-4 h-4" />
              <span className="font-medium">{stats.total_views} Views</span>
            </div>
          </div>
        )}
      </div>

      {/* Main Content Tabs */}
      <Card className="p-6">
        <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as TabValue)}>
          <TabsList className="grid w-full grid-cols-3 mb-6">
            <TabsTrigger value="updates" className="flex items-center gap-2">
              <List className="w-4 h-4" />
              All Updates
            </TabsTrigger>
            <TabsTrigger value="create" className="flex items-center gap-2">
              <PlusCircle className="w-4 h-4" />
              Create Update
            </TabsTrigger>
            <TabsTrigger value="statistics" className="flex items-center gap-2">
              <BarChart2 className="w-4 h-4" />
              Statistics
            </TabsTrigger>
          </TabsList>

          <TabsContent value="updates" className="space-y-4">
            <div className="space-y-4">
              {updates.length === 0 ? (
                <div className="text-center py-12">
                  <p className="text-muted-foreground">No platform updates found</p>
                  <Button onClick={() => setActiveTab('create')} className="mt-4">
                    <PlusCircle className="w-4 h-4 mr-2" />
                    Create First Update
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  {updates.map((update) => (
                    <Card key={update.id} className="p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <Badge variant={update.is_published ? "default" : "secondary"}>
                              {update.is_published ? "Published" : "Draft"}
                            </Badge>
                            <Badge variant={
                              update.priority === 'HIGH' ? 'destructive' :
                              update.priority === 'CRITICAL' ? 'destructive' :
                              update.priority === 'LOW' ? 'secondary' : 'default'
                            }>
                              {update.priority}
                            </Badge>
                            <Badge variant="outline">
                              {update.update_type}
                            </Badge>
                            <Badge variant="outline">
                              {update.target_audience}
                            </Badge>
                          </div>
                          
                          <h3 className="text-lg font-semibold mb-2">{update.title}</h3>
                          <p className="text-muted-foreground mb-3 line-clamp-2">{update.description}</p>
                          
                          <div className="flex items-center gap-4 text-sm text-muted-foreground">
                            <div className="flex items-center gap-1">
                              <Eye className="w-3 h-3" />
                              <span>{update.view_count} views</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Calendar className="w-3 h-3" />
                              <span>{new Date(update.created_at).toLocaleDateString()}</span>
                            </div>
                            {update.media_type !== 'NONE' && (
                              <div className="flex items-center gap-1">
                                <span>{update.media_type} ({update.media_urls.length})</span>
                              </div>
                            )}
                          </div>
                        </div>
                        
                        <div className="flex items-center gap-2 ml-4">
                          <Button 
                            variant="outline" 
                            size="sm" 
                            onClick={() => handleEdit(update)}
                          >
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button 
                            variant="outline" 
                            size="sm" 
                            onClick={() => handleDelete(update.id)}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                          <Switch 
                            checked={update.is_published}
                            onCheckedChange={() => handlePublishToggle(update.id, update.is_published)}
                            disabled={loading}
                          />
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="create" className="space-y-4">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Title</label>
                    <Input 
                      name="title" 
                      value={formData.title} 
                      onChange={handleInputChange} 
                      placeholder="Update title" 
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-2">Update Type</label>
                    <Select 
                      value={formData.update_type} 
                      onValueChange={(value) => handleSelectChange('update_type', value as UpdateType)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select update type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="FEATURE">Feature</SelectItem>
                        <SelectItem value="BUG_FIX">Bug Fix</SelectItem>
                        <SelectItem value="ANNOUNCEMENT">Announcement</SelectItem>
                        <SelectItem value="MAINTENANCE">Maintenance</SelectItem>
                        <SelectItem value="SECURITY">Security</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-2">Priority</label>
                    <Select 
                      value={formData.priority} 
                      onValueChange={(value) => handleSelectChange('priority', value as UpdatePriority)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select priority" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="LOW">Low</SelectItem>
                        <SelectItem value="NORMAL">Normal</SelectItem>
                        <SelectItem value="HIGH">High</SelectItem>
                        <SelectItem value="CRITICAL">Critical</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Target Audience</label>
                    <Select 
                      value={formData.target_audience} 
                      onValueChange={(value) => handleSelectChange('target_audience', value as TargetAudience)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select audience" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="ALL">All Users</SelectItem>
                        <SelectItem value="ADMIN">Admins Only</SelectItem>
                        <SelectItem value="USER">Regular Users</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-2">Media Type</label>
                    <Select 
                      value={formData.media_type} 
                      onValueChange={(value) => handleSelectChange('media_type', value as 'IMAGE' | 'VIDEO' | 'NONE')}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select media type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="NONE">None</SelectItem>
                        <SelectItem value="IMAGE">Image</SelectItem>
                        <SelectItem value="VIDEO">Video</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-2">Thumbnail URL</label>
                    <Input 
                      name="thumbnail_url" 
                      value={formData.thumbnail_url} 
                      onChange={handleInputChange} 
                      placeholder="https://example.com/thumbnail.jpg"
                    />
                  </div>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Description</label>
                <Textarea 
                  name="description" 
                  value={formData.description} 
                  onChange={handleInputChange} 
                  placeholder="Update description with details..." 
                  rows={6} 
                  required
                />
              </div>
              
              {formData.media_type !== 'NONE' && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Media URLs</label>
                    <div className="flex gap-2">
                      <Input 
                        value={mediaUrlInput} 
                        onChange={(e) => setMediaUrlInput(e.target.value)} 
                        placeholder="https://example.com/media.jpg"
                      />
                      <Button type="button" onClick={addMediaUrl} size="sm">
                        Add URL
                      </Button>
                    </div>
                  </div>
                  
                  {formData.media_urls.length > 0 && (
                    <div className="space-y-2">
                      {formData.media_urls.map((url, index) => (
                        <div key={index} className="flex items-center gap-2 p-2 bg-secondary rounded">
                          <span className="flex-1 truncate">{url}</span>
                          <Button 
                            type="button" 
                            variant="ghost" 
                            size="sm" 
                            onClick={() => removeMediaUrl(index)}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
              
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <Switch 
                    id="publish-switch" 
                    checked={formData.is_published} 
                    onCheckedChange={(checked) => handleSwitchChange('is_published', checked)}
                  />
                  <label htmlFor="publish-switch" className="text-sm font-medium">
                    Publish Immediately
                  </label>
                </div>
                
                {formData.is_published && (
                  <div>
                    <label className="block text-sm font-medium mb-2">Expires At (Optional)</label>
                    <Input 
                      name="expires_at" 
                      type="datetime-local" 
                      value={formData.expires_at || ''} 
                      onChange={handleInputChange}
                    />
                  </div>
                )}
              </div>
              
              <div className="flex gap-4 justify-end">
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => setActiveTab('updates')}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={loading}>
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin mr-2" />
                      Saving...
                    </>
                  ) : (
                    <>
                      {formData.id ? (
                        <>
                          <Edit className="w-4 h-4 mr-2" />
                          Update
                        </>
                      ) : (
                        <>
                          <PlusCircle className="w-4 h-4 mr-2" />
                          Create Update
                        </>
                      )}
                    </>
                  )}
                </Button>
              </div>
            </form>
          </TabsContent>

          <TabsContent value="statistics" className="space-y-4">
            {stats && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* Total Updates Card */}
                <Card className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold">Total Updates</h3>
                      <p className="text-3xl font-bold mt-2">{stats.total_updates}</p>
                    </div>
                    <Megaphone className="w-8 h-8 text-blue-500" />
                  </div>
                </Card>

                {/* Published Updates Card */}
                <Card className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold">Published</h3>
                      <p className="text-3xl font-bold mt-2">{stats.published_updates}</p>
                    </div>
                    <CheckCircle className="w-8 h-8 text-green-500" />
                  </div>
                </Card>

                {/* Draft Updates Card */}
                <Card className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold">Drafts</h3>
                      <p className="text-3xl font-bold mt-2">{stats.draft_updates}</p>
                    </div>
                    <Clock className="w-8 h-8 text-yellow-500" />
                  </div>
                </Card>

                {/* Total Views Card */}
                <Card className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold">Total Views</h3>
                      <p className="text-3xl font-bold mt-2">{stats.total_views}</p>
                    </div>
                    <Eye className="w-8 h-8 text-purple-500" />
                  </div>
                </Card>

                {/* Updates by Type */}
                <Card className="p-6 md:col-span-2">
                  <h3 className="text-lg font-semibold mb-4">Updates by Type</h3>
                  <div className="space-y-3">
                    {Object.entries(stats.by_type).map(([type, count]) => (
                      <div key={type} className="flex items-center justify-between p-3 bg-secondary rounded-lg">
                        <div className="flex items-center gap-3">
                          <span className="font-medium">{type}</span>
                        </div>
                        <div className="flex items-center gap-4">
                          <span className="text-muted-foreground">{count} updates</span>
                          <div className="w-24 h-2 bg-primary rounded-full">
                            <div 
                              className="h-full bg-primary-foreground rounded-full"
                              style={{ width: `${(count / stats.total_updates) * 100}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>

                {/* Updates by Priority */}
                <Card className="p-6">
                  <h3 className="text-lg font-semibold mb-4">Updates by Priority</h3>
                  <div className="space-y-3">
                    {Object.entries(stats.by_priority).map(([priority, count]) => (
                      <div key={priority} className="flex items-center justify-between p-3 bg-secondary rounded-lg">
                        <div className="flex items-center gap-3">
                          <Badge variant={
                            priority === 'HIGH' ? 'destructive' :
                            priority === 'CRITICAL' ? 'destructive' :
                            priority === 'LOW' ? 'secondary' : 'default'
                          }>
                            {priority}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-muted-foreground">{count} updates</span>
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