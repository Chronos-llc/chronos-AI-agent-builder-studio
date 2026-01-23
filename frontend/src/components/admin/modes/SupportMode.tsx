import { useState, useEffect } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../ui/tabs'
import { Card } from '../../ui/card'
import { Alert, AlertDescription } from '../../ui/alert'
import { 
  AlertCircle, 
  Loader2, 
  PlusCircle, 
  List,
  MessageCircle,
  BarChart2,
  Search,
  Edit,
  Trash2,
  CheckCircle,
  XCircle,
  Clock,
  Mail,
  User,
  Shield
} from 'lucide-react'
import { Button } from '../../ui/button'
import { Input } from '../../ui/input'
import { Textarea } from '../../ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../ui/select'
import { Badge } from '../../ui/badge'
import { toast } from 'react-hot-toast'
import { SupportMessage, SupportStatus, SupportPriority, SupportCategory } from '../../../types/support'

// Mock data and functions - these would be replaced with actual API calls
type TabValue = 'tickets' | 'create' | 'statistics'

export const SupportMode = () => {
  const [activeTab, setActiveTab] = useState<TabValue>('tickets')
  const [messages, setMessages] = useState<SupportMessage[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [stats, setStats] = useState<any>(null)
  const [selectedMessage, setSelectedMessage] = useState<SupportMessage | null>(null)
  const [replyText, setReplyText] = useState('')


  // Form state for creating/editing messages
  const [formData, setFormData] = useState({
    id: null as number | null,
    subject: '',
    message: '',
    priority: SupportPriority.NORMAL,
    category: SupportCategory.OTHER
  })

  // Filter and search state
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<SupportStatus | 'ALL'>('ALL')
  const [priorityFilter, setPriorityFilter] = useState<SupportPriority | 'ALL'>('ALL')
  const [categoryFilter, setCategoryFilter] = useState<SupportCategory | 'ALL'>('ALL')

  useEffect(() => {
    loadMessages()
    loadStatistics()
  }, [])

  const loadMessages = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Mock API call - replace with actual API
      const mockMessages: SupportMessage[] = [
        {
          id: 1,
          user_id: 101,
          subject: "Login Issue",
          message: "I can't login to my account. It keeps saying invalid credentials even though I'm sure I'm using the right password.",
          status: SupportStatus.OPEN,
          priority: SupportPriority.HIGH,
          category: SupportCategory.TECHNICAL,
          assigned_to: null,
          created_at: '2026-01-10T09:30:00Z',
          updated_at: '2026-01-10T09:30:00Z',
          resolved_at: null,
          user: {
            id: 101,
            name: 'John Doe',
            email: 'john@example.com'
          },
          replies: []
        },
        {
          id: 2,
          user_id: 102,
          subject: "Billing Question",
          message: "I was charged twice for my subscription. Can you please check and refund the duplicate charge?",
          status: SupportStatus.IN_PROGRESS,
          priority: SupportPriority.NORMAL,
          category: SupportCategory.BILLING,
          assigned_to: 1,
          created_at: '2026-01-09T14:15:00Z',
          updated_at: '2026-01-10T10:45:00Z',
          resolved_at: null,
          user: {
            id: 102,
            name: 'Jane Smith',
            email: 'jane@example.com'
          },
          replies: [
            {
              id: 1,
              message_id: 2,
              user_id: 1,
              is_admin: true,
              reply_text: "Thank you for reporting this. I'll check with our billing team and get back to you shortly.",
              created_at: '2026-01-10T10:45:00Z',
              user: {
                id: 1,
                name: 'Support Admin',
                email: 'support@chronos.ai'
              }
            }
          ]
        },
        {
          id: 3,
          user_id: 103,
          subject: "Feature Request",
          message: "It would be great if you could add dark mode support to the platform. Many users would appreciate this feature.",
          status: SupportStatus.OPEN,
          priority: SupportPriority.LOW,
          category: SupportCategory.FEATURE_REQUEST,
          assigned_to: null,
          created_at: '2026-01-08T11:20:00Z',
          updated_at: '2026-01-08T11:20:00Z',
          resolved_at: null,
          user: {
            id: 103,
            name: 'Bob Johnson',
            email: 'bob@example.com'
          },
          replies: []
        }
      ]
      
      setMessages(mockMessages)
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load support messages')
      console.error('Error loading support messages:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadStatistics = async () => {
    try {
      // Mock statistics
      const mockStats = {
        total_tickets: 12,
        open_tickets: 5,
        in_progress_tickets: 3,
        resolved_tickets: 3,
        closed_tickets: 1,
        by_status: {
          [SupportStatus.OPEN]: 5,
          [SupportStatus.IN_PROGRESS]: 3,
          [SupportStatus.RESOLVED]: 3,
          [SupportStatus.CLOSED]: 1
        },
        by_priority: {
          [SupportPriority.LOW]: 2,
          [SupportPriority.NORMAL]: 6,
          [SupportPriority.HIGH]: 3,
          [SupportPriority.CRITICAL]: 1
        },
        by_category: {
          [SupportCategory.BUG]: 2,
          [SupportCategory.FEATURE_REQUEST]: 3,
          [SupportCategory.BILLING]: 2,
          [SupportCategory.TECHNICAL]: 3,
          [SupportCategory.ACCOUNT]: 1,
          [SupportCategory.OTHER]: 1
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      setLoading(true)
      
      // Mock API call
      if (formData.id) {
        // Update existing
        toast.success("Support message has been successfully updated.")
      } else {
        // Create new
        const newMessage: SupportMessage = {
          id: messages.length + 1,
          user_id: 104, // Mock user ID
          subject: formData.subject,
          message: formData.message,
          status: SupportStatus.OPEN,
          priority: formData.priority,
          category: formData.category,
          assigned_to: null,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          resolved_at: null,
          user: {
            id: 104,
            name: 'New User',
            email: 'newuser@example.com'
          },
          replies: []
        }
        
        setMessages([...messages, newMessage])
        
        toast.success("New support message has been successfully created.")
        
        // Reset form
        setFormData({
          id: null,
          subject: '',
          message: '',
          priority: SupportPriority.NORMAL,
          category: SupportCategory.OTHER
        })
      }
      
      setActiveTab('tickets')
      
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to save message')
      console.error('Error saving message:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleEdit = (message: SupportMessage) => {
    setFormData({
      id: message.id,
      subject: message.subject,
      message: message.message,
      priority: message.priority,
      category: message.category
    })
    setActiveTab('create')
  }

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this support message?')) {
      try {
        setLoading(true)
        // Mock API call
        setMessages(messages.filter(message => message.id !== id))
        
        toast.success("Support message has been successfully deleted.")
        
      } catch (err) {
        toast.error(err instanceof Error ? err.message : 'Failed to delete message')
        console.error('Error deleting message:', err)
      } finally {
        setLoading(false)
      }
    }
  }

  const handleStatusChange = async (id: number, newStatus: SupportStatus) => {
    try {
      setLoading(true)
      // Mock API call
      setMessages(messages.map(message => 
        message.id === id ? {
          ...message,
          status: newStatus,
          resolved_at: newStatus === 'RESOLVED' ? new Date().toISOString() : null
        } : message
      ))
      
      toast.success(`Message status has been changed to ${newStatus}.`)
      
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to update status')
      console.error('Error updating status:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleAssign = async (id: number) => {
    try {
      setLoading(true)
      // Mock API call - assign to current admin (ID 1)
      setMessages(messages.map(message => 
        message.id === id ? {
          ...message,
          assigned_to: 1,
          status: 'IN_PROGRESS'
        } : message
      ))
      
      toast.success("Message has been assigned to you.")
      
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to assign message')
      console.error('Error assigning message:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleReply = async (messageId: number) => {
    if (!replyText.trim()) return
    
    try {
      setLoading(true)
      // Mock API call
      setMessages(messages.map(message => 
        message.id === messageId ? {
          ...message,
          replies: [...message.replies, {
            id: message.replies.length + 1,
            message_id: messageId,
            user_id: 1, // Current admin
            is_admin: true,
            reply_text: replyText,
            created_at: new Date().toISOString(),
            user: {
              id: 1,
              name: 'Support Admin',
              email: 'support@chronos.ai'
            }
          }]
        } : message
      ))
      
      setReplyText('')
      
      toast.success("Your reply has been successfully sent.")
      
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to send reply')
      console.error('Error sending reply:', err)
    } finally {
      setLoading(false)
    }
  }

  const filteredMessages = messages.filter(message => {
    // Search filter
    if (searchQuery && 
        !message.subject.toLowerCase().includes(searchQuery.toLowerCase()) &&
        !message.message.toLowerCase().includes(searchQuery.toLowerCase()) &&
        !message.user.name.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false
    }
    
    // Status filter
    if (statusFilter !== 'ALL' && message.status !== statusFilter) {
      return false
    }
    
    // Priority filter
    if (priorityFilter !== 'ALL' && message.priority !== priorityFilter) {
      return false
    }
    
    // Category filter
    if (categoryFilter !== 'ALL' && message.category !== categoryFilter) {
      return false
    }
    
    return true
  })

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
          <p className="text-muted-foreground">Loading Support Messages...</p>
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
            onClick={loadMessages}
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
          <h1 className="text-3xl font-bold">Support Management</h1>
          <p className="text-muted-foreground mt-1">
            Manage user support tickets and provide assistance
          </p>
        </div>
        
        {/* Statistics Badges */}
        {stats && (
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
              <MessageCircle className="w-4 h-4" />
              <span className="font-medium">{stats.total_tickets} Tickets</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">
              <AlertCircle className="w-4 h-4" />
              <span className="font-medium">{stats.open_tickets} Open</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
              <CheckCircle className="w-4 h-4" />
              <span className="font-medium">{stats.resolved_tickets} Resolved</span>
            </div>
          </div>
        )}
      </div>

      {/* Main Content Tabs */}
      <Card className="p-6">
        <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as TabValue)}>
          <TabsList className="grid w-full grid-cols-3 mb-6">
            <TabsTrigger value="tickets" className="flex items-center gap-2">
              <List className="w-4 h-4" />
              All Tickets
            </TabsTrigger>
            <TabsTrigger value="create" className="flex items-center gap-2">
              <PlusCircle className="w-4 h-4" />
              Create Ticket
            </TabsTrigger>
            <TabsTrigger value="statistics" className="flex items-center gap-2">
              <BarChart2 className="w-4 h-4" />
              Statistics
            </TabsTrigger>
          </TabsList>

          <TabsContent value="tickets" className="space-y-4">
            {/* Filters */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium mb-2">Search</label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input 
                    placeholder="Search tickets..." 
                    value={searchQuery} 
                    onChange={(e) => setSearchQuery(e.target.value)} 
                    className="pl-10"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Status</label>
                <Select value={statusFilter} onValueChange={(value) => setStatusFilter(value as SupportStatus | 'ALL')}>
                  <SelectTrigger>
                    <SelectValue placeholder="All Statuses" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ALL">All Statuses</SelectItem>
                    <SelectItem value="OPEN">Open</SelectItem>
                    <SelectItem value="IN_PROGRESS">In Progress</SelectItem>
                    <SelectItem value="RESOLVED">Resolved</SelectItem>
                    <SelectItem value="CLOSED">Closed</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Priority</label>
                <Select value={priorityFilter} onValueChange={(value) => setPriorityFilter(value as SupportPriority | 'ALL')}>
                  <SelectTrigger>
                    <SelectValue placeholder="All Priorities" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ALL">All Priorities</SelectItem>
                    <SelectItem value="LOW">Low</SelectItem>
                    <SelectItem value="NORMAL">Normal</SelectItem>
                    <SelectItem value="HIGH">High</SelectItem>
                    <SelectItem value="CRITICAL">Critical</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Category</label>
                <Select value={categoryFilter} onValueChange={(value) => setCategoryFilter(value as SupportCategory | 'ALL')}>
                  <SelectTrigger>
                    <SelectValue placeholder="All Categories" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ALL">All Categories</SelectItem>
                    <SelectItem value="BUG">Bug</SelectItem>
                    <SelectItem value="FEATURE_REQUEST">Feature Request</SelectItem>
                    <SelectItem value="BILLING">Billing</SelectItem>
                    <SelectItem value="TECHNICAL">Technical</SelectItem>
                    <SelectItem value="ACCOUNT">Account</SelectItem>
                    <SelectItem value="OTHER">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div className="space-y-4">
              {filteredMessages.length === 0 ? (
                <div className="text-center py-12">
                  <p className="text-muted-foreground">No support messages found</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {filteredMessages.map((message) => (
                    <Card key={message.id} className="p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <Badge variant={
                              message.status === 'OPEN' ? 'default' :
                              message.status === 'IN_PROGRESS' ? 'secondary' :
                              message.status === 'RESOLVED' ? 'success' :
                              'outline'
                            }>
                              {message.status}
                            </Badge>
                            <Badge variant={
                              message.priority === 'HIGH' ? 'destructive' :
                              message.priority === 'CRITICAL' ? 'destructive' :
                              message.priority === 'LOW' ? 'secondary' : 'default'
                            }>
                              {message.priority}
                            </Badge>
                            <Badge variant="outline">
                              {message.category}
                            </Badge>
                            {message.assigned_to && (
                              <Badge variant="outline" className="flex items-center gap-1">
                                <Shield className="w-3 h-3" />
                                <span>Assigned</span>
                              </Badge>
                            )}
                          </div>
                          
                          <h3 className="text-lg font-semibold mb-2">{message.subject}</h3>
                          <p className="text-muted-foreground mb-3 line-clamp-2">{message.message}</p>
                          
                          <div className="flex items-center gap-4 text-sm text-muted-foreground">
                            <div className="flex items-center gap-1">
                              <User className="w-3 h-3" />
                              <span>{message.user.name}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Mail className="w-3 h-3" />
                              <span>{message.user.email}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              <span>{new Date(message.created_at).toLocaleString()}</span>
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex items-center gap-2 ml-4">
                          <Button 
                            variant="outline" 
                            size="sm" 
                            onClick={() => {
                              setSelectedMessage(message)
                              setActiveTab('tickets')
                            }}
                          >
                            <MessageCircle className="w-4 h-4" />
                          </Button>
                          <Button 
                            variant="outline" 
                            size="sm" 
                            onClick={() => handleEdit(message)}
                          >
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button 
                            variant="outline" 
                            size="sm" 
                            onClick={() => handleDelete(message.id)}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
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
                    <label className="block text-sm font-medium mb-2">Subject</label>
                    <Input 
                      name="subject" 
                      value={formData.subject} 
                      onChange={handleInputChange} 
                      placeholder="Support request subject" 
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-2">Priority</label>
                    <Select 
                      value={formData.priority} 
                      onValueChange={(value) => handleSelectChange('priority', value as SupportPriority)}
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
                    <label className="block text-sm font-medium mb-2">Category</label>
                    <Select 
                      value={formData.category} 
                      onValueChange={(value) => handleSelectChange('category', value as SupportCategory)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select category" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="BUG">Bug</SelectItem>
                        <SelectItem value="FEATURE_REQUEST">Feature Request</SelectItem>
                        <SelectItem value="BILLING">Billing</SelectItem>
                        <SelectItem value="TECHNICAL">Technical</SelectItem>
                        <SelectItem value="ACCOUNT">Account</SelectItem>
                        <SelectItem value="OTHER">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Message</label>
                <Textarea 
                  name="message" 
                  value={formData.message} 
                  onChange={handleInputChange} 
                  placeholder="Describe the issue or request in detail..." 
                  rows={8} 
                  required
                />
              </div>
              
              <div className="flex gap-4 justify-end">
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => setActiveTab('tickets')}
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
                          Update Ticket
                        </>
                      ) : (
                        <>
                          <PlusCircle className="w-4 h-4 mr-2" />
                          Create Ticket
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
                {/* Total Tickets Card */}
                <Card className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold">Total Tickets</h3>
                      <p className="text-3xl font-bold mt-2">{stats.total_tickets}</p>
                    </div>
                    <MessageCircle className="w-8 h-8 text-blue-500" />
                  </div>
                </Card>

                {/* Open Tickets Card */}
                <Card className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold">Open Tickets</h3>
                      <p className="text-3xl font-bold mt-2">{stats.open_tickets}</p>
                    </div>
                    <AlertCircle className="w-8 h-8 text-red-500" />
                  </div>
                </Card>

                {/* In Progress Tickets Card */}
                <Card className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold">In Progress</h3>
                      <p className="text-3xl font-bold mt-2">{stats.in_progress_tickets}</p>
                    </div>
                    <Clock className="w-8 h-8 text-yellow-500" />
                  </div>
                </Card>

                {/* Resolved Tickets Card */}
                <Card className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold">Resolved</h3>
                      <p className="text-3xl font-bold mt-2">{stats.resolved_tickets}</p>
                    </div>
                    <CheckCircle className="w-8 h-8 text-green-500" />
                  </div>
                </Card>

                {/* Closed Tickets Card */}
                <Card className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold">Closed</h3>
                      <p className="text-3xl font-bold mt-2">{stats.closed_tickets}</p>
                    </div>
                    <XCircle className="w-8 h-8 text-gray-500" />
                  </div>
                </Card>

                {/* Tickets by Status */}
                <Card className="p-6 md:col-span-2">
                  <h3 className="text-lg font-semibold mb-4">Tickets by Status</h3>
                  <div className="space-y-3">
                    {Object.entries(stats.by_status).map(([status, count]) => (
                      <div key={status} className="flex items-center justify-between p-3 bg-secondary rounded-lg">
                        <div className="flex items-center gap-3">
                          <Badge variant={
                            status === 'OPEN' ? 'default' :
                            status === 'IN_PROGRESS' ? 'secondary' :
                            status === 'RESOLVED' ? 'success' :
                            'outline'
                          }>
                            {status}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-4">
                          <span className="text-muted-foreground">{count} tickets</span>
                          <div className="w-24 h-2 bg-primary rounded-full">
                            <div 
                              className="h-full bg-primary-foreground rounded-full"
                              style={{ width: `${(count / stats.total_tickets) * 100}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>

                {/* Tickets by Priority */}
                <Card className="p-6">
                  <h3 className="text-lg font-semibold mb-4">Tickets by Priority</h3>
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
                          <span className="text-muted-foreground">{count} tickets</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>

                {/* Tickets by Category */}
                <Card className="p-6">
                  <h3 className="text-lg font-semibold mb-4">Tickets by Category</h3>
                  <div className="space-y-3">
                    {Object.entries(stats.by_category).map(([category, count]) => (
                      <div key={category} className="flex items-center justify-between p-3 bg-secondary rounded-lg">
                        <div className="flex items-center gap-3">
                          <span className="font-medium">{category}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-muted-foreground">{count} tickets</span>
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