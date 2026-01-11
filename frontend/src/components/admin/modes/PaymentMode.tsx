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
  CreditCard,
  DollarSign,
  BarChart2,
  Edit,
  Trash2,
  CheckCircle,
  XCircle,
  Shield,
  Globe,
  Percent
} from 'lucide-react'
import { Button } from '../../ui/button'
import { Input } from '../../ui/input'
import { Textarea } from '../../ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../ui/select'
import { Switch } from '../../ui/switch'
import { Badge } from '../../ui/badge'
import { useToast } from '../../ui/use-toast'
import type { PaymentMethod, PaymentSettings, PaymentProvider } from '../../../types/payment'

// Mock data and functions - these would be replaced with actual API calls
type TabValue = 'methods' | 'settings' | 'transactions' | 'statistics'

export const PaymentMode = () => {
  const [activeTab, setActiveTab] = useState<TabValue>('methods')
  const [methods, setMethods] = useState<PaymentMethod[]>([])
  const [settings, setSettings] = useState<PaymentSettings | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [stats, setStats] = useState<any>(null)
  const { toast } = useToast()

  // Form state for creating/editing payment methods
  const [formData, setFormData] = useState({
    id: null as number | null,
    name: '',
    provider: 'stripe' as PaymentProvider,
    is_active: true,
    configuration: {} as Record<string, any>
  })

  // Form state for payment settings
  const [settingsFormData, setSettingsFormData] = useState({
    currency: 'USD',
    tax_rate: 0.0,
    default_payment_method_id: null as number | null,
    settings: {} as Record<string, any>
  })

  useEffect(() => {
    loadMethods()
    loadSettings()
    loadStatistics()
  }, [])

  const loadMethods = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Mock API call - replace with actual API
      const mockMethods: PaymentMethod[] = [
        {
          id: 1,
          name: "Stripe Credit Card",
          provider: "stripe",
          is_active: true,
          configuration: {
            api_key: "sk_test_123456789",
            webhook_secret: "whsec_123456789",
            supported_currencies: ["USD", "EUR", "GBP"]
          },
          created_at: '2026-01-01T10:00:00Z',
          updated_at: '2026-01-01T10:00:00Z'
        },
        {
          id: 2,
          name: "PayPal",
          provider: "paypal",
          is_active: true,
          configuration: {
            client_id: "paypal_client_123",
            client_secret: "paypal_secret_456",
            sandbox: false
          },
          created_at: '2026-01-02T11:30:00Z',
          updated_at: '2026-01-02T11:30:00Z'
        },
        {
          id: 3,
          name: "Bank Transfer",
          provider: "bank",
          is_active: false,
          configuration: {
            account_number: "123456789",
            routing_number: "987654321",
            bank_name: "Chase Bank"
          },
          created_at: '2026-01-03T09:15:00Z',
          updated_at: '2026-01-03T09:15:00Z'
        }
      ]
      
      setMethods(mockMethods)
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load payment methods')
      console.error('Error loading payment methods:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadSettings = async () => {
    try {
      // Mock API call - replace with actual API
      const mockSettings: PaymentSettings = {
        id: 1,
        currency: "USD",
        tax_rate: 8.5,
        default_payment_method_id: 1,
        settings: {
          auto_invoice: true,
          invoice_prefix: "INV-",
          due_days: 30
        },
        updated_at: '2026-01-10T08:45:00Z'
      }
      
      setSettings(mockSettings)
      setSettingsFormData({
        currency: mockSettings.currency,
        tax_rate: mockSettings.tax_rate,
        default_payment_method_id: mockSettings.default_payment_method_id,
        settings: mockSettings.settings
      })
      
    } catch (err) {
      console.error('Error loading payment settings:', err)
    }
  }

  const loadStatistics = async () => {
    try {
      // Mock statistics
      const mockStats = {
        active_methods: 2,
        inactive_methods: 1,
        total_transactions: 42,
        total_revenue: 12500.75,
        by_provider: {
          stripe: 1,
          paypal: 1,
          bank: 1,
          credit_card: 0,
          crypto: 0
        },
        recent_transactions: [
          {
            id: 1,
            user_id: 101,
            amount: 99.99,
            currency: "USD",
            payment_method_id: 1,
            transaction_type: "SUBSCRIPTION",
            status: "COMPLETED",
            created_at: '2026-01-10T14:30:00Z',
            updated_at: '2026-01-10T14:30:00Z',
            user: {
              id: 101,
              name: 'John Doe',
              email: 'john@example.com'
            },
            method: {
              id: 1,
              name: 'Stripe Credit Card',
              provider: 'stripe'
            }
          },
          {
            id: 2,
            user_id: 102,
            amount: 49.99,
            currency: "USD",
            payment_method_id: 2,
            transaction_type: "ONE_TIME",
            status: "COMPLETED",
            created_at: '2026-01-09T10:15:00Z',
            updated_at: '2026-01-09T10:15:00Z',
            user: {
              id: 102,
              name: 'Jane Smith',
              email: 'jane@example.com'
            },
            method: {
              id: 2,
              name: 'PayPal',
              provider: 'paypal'
            }
          }
        ]
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

  const handleSettingsInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setSettingsFormData(prev => ({ ...prev, [name]: name === 'tax_rate' ? parseFloat(value) || 0 : value }))
  }

  const handleSelectChange = (name: string, value: string) => {
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSettingsSelectChange = (name: string, value: string) => {
    setSettingsFormData(prev => ({ ...prev, [name]: name === 'default_payment_method_id' ? parseInt(value) : value }))
  }

  const handleSwitchChange = (name: string, checked: boolean) => {
    setFormData(prev => ({ ...prev, [name]: checked }))
  }

  const handleMethodSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      setLoading(true)
      
      // Mock API call
      if (formData.id) {
        // Update existing
        toast({
          title: "Payment Method Updated",
          description: "Payment method has been successfully updated.",
          variant: "success"
        })
      } else {
        // Create new
        const newMethod: PaymentMethod = {
          id: methods.length + 1,
          name: formData.name,
          provider: formData.provider,
          is_active: formData.is_active,
          configuration: formData.configuration,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
        
        setMethods([...methods, newMethod])
        
        toast({
          title: "Payment Method Created",
          description: "New payment method has been successfully created.",
          variant: "success"
        })
        
        // Reset form
        setFormData({
          id: null,
          name: '',
          provider: 'stripe',
          is_active: true,
          configuration: {}
        })
      }
      
      setActiveTab('methods')
      
    } catch (err) {
      toast({
        title: "Error",
        description: err instanceof Error ? err.message : 'Failed to save payment method',
        variant: "destructive"
      })
      console.error('Error saving payment method:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSettingsSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      setLoading(true)
      
      // Mock API call
      const updatedSettings: PaymentSettings = {
        id: 1,
        currency: settingsFormData.currency,
        tax_rate: settingsFormData.tax_rate,
        default_payment_method_id: settingsFormData.default_payment_method_id,
        settings: settingsFormData.settings,
        updated_at: new Date().toISOString()
      }
      
      setSettings(updatedSettings)
      
      toast({
        title: "Settings Updated",
        description: "Payment settings have been successfully updated.",
        variant: "success"
      })
      
    } catch (err) {
      toast({
        title: "Error",
        description: err instanceof Error ? err.message : 'Failed to update settings',
        variant: "destructive"
      })
      console.error('Error updating settings:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleEdit = (method: PaymentMethod) => {
    setFormData({
      id: method.id,
      name: method.name,
      provider: method.provider,
      is_active: method.is_active,
      configuration: method.configuration
    })
    setActiveTab('methods')
  }

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this payment method?')) {
      try {
        setLoading(true)
        // Mock API call
        setMethods(methods.filter(method => method.id !== id))
        
        toast({
          title: "Payment Method Deleted",
          description: "Payment method has been successfully deleted.",
          variant: "success"
        })
        
      } catch (err) {
        toast({
          title: "Error",
          description: err instanceof Error ? err.message : 'Failed to delete payment method',
          variant: "destructive"
        })
        console.error('Error deleting payment method:', err)
      } finally {
        setLoading(false)
      }
    }
  }

  const handleToggleActive = async (id: number, currentStatus: boolean) => {
    try {
      setLoading(true)
      // Mock API call
      setMethods(methods.map(method => 
        method.id === id ? { ...method, is_active: !currentStatus } : method
      ))
      
      toast({
        title: "Status Updated",
        description: `Payment method has been ${!currentStatus ? 'activated' : 'deactivated'}.`,
        variant: "success"
      })
      
    } catch (err) {
      toast({
        title: "Error",
        description: err instanceof Error ? err.message : 'Failed to update status',
        variant: "destructive"
      })
      console.error('Error updating status:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
          <p className="text-muted-foreground">Loading Payment Methods...</p>
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
            onClick={loadMethods}
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
          <h1 className="text-3xl font-bold">Payment Management</h1>
          <p className="text-muted-foreground mt-1">
            Configure and manage payment methods and settings
          </p>
        </div>
        
        {/* Statistics Badges */}
        {stats && (
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
              <CreditCard className="w-4 h-4" />
              <span className="font-medium">{stats.active_methods} Active</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
              <DollarSign className="w-4 h-4" />
              <span className="font-medium">${stats.total_revenue.toLocaleString()}</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
              <Globe className="w-4 h-4" />
              <span className="font-medium">{stats.by_provider.stripe + stats.by_provider.paypal} Gateways</span>
            </div>
          </div>
        )}
      </div>

      {/* Main Content Tabs */}
      <Card className="p-6">
        <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as TabValue)}>
          <TabsList className="grid w-full grid-cols-4 mb-6">
            <TabsTrigger value="methods" className="flex items-center gap-2">
              <List className="w-4 h-4" />
              Payment Methods
            </TabsTrigger>
            <TabsTrigger value="settings" className="flex items-center gap-2">
              <Settings className="w-4 h-4" />
              Payment Settings
            </TabsTrigger>
            <TabsTrigger value="transactions" className="flex items-center gap-2">
              <CreditCard className="w-4 h-4" />
              Transactions
            </TabsTrigger>
            <TabsTrigger value="statistics" className="flex items-center gap-2">
              <BarChart2 className="w-4 h-4" />
              Statistics
            </TabsTrigger>
          </TabsList>

          <TabsContent value="methods" className="space-y-4">
            <div className="flex justify-end mb-4">
              <Button onClick={() => {
                setFormData({
                  id: null,
                  name: '',
                  provider: 'stripe',
                  is_active: true,
                  configuration: {}
                })
                setActiveTab('methods')
              }}>
                <PlusCircle className="w-4 h-4 mr-2" />
                Add Payment Method
              </Button>
            </div>
            
            <div className="space-y-4">
              {methods.length === 0 ? (
                <div className="text-center py-12">
                  <p className="text-muted-foreground">No payment methods found</p>
                  <Button onClick={() => setActiveTab('methods')} className="mt-4">
                    <PlusCircle className="w-4 h-4 mr-2" />
                    Add First Method
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  {methods.map((method) => (
                    <Card key={method.id} className="p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <Badge variant={method.is_active ? "default" : "secondary"}>
                              {method.is_active ? "Active" : "Inactive"}
                            </Badge>
                            <Badge variant="outline">
                              {method.provider.toUpperCase()}
                            </Badge>
                          </div>
                          
                          <h3 className="text-lg font-semibold mb-2">{method.name}</h3>
                          <p className="text-muted-foreground mb-3">
                            {method.provider.charAt(0).toUpperCase() + method.provider.slice(1)} Payment Gateway
                          </p>
                          
                          <div className="text-sm text-muted-foreground mb-3">
                            <div className="font-medium mb-1">Configuration:</div>
                            <div className="grid grid-cols-2 gap-2">
                              {Object.entries(method.configuration).map(([key, value]) => (
                                <div key={key} className="flex items-center gap-1">
                                  <span className="font-medium">{key}:</span>
                                  <span className="truncate">{typeof value === 'object' ? JSON.stringify(value) : String(value)}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                          
                          <div className="flex items-center gap-4 text-sm text-muted-foreground">
                            <div className="flex items-center gap-1">
                              <span>Created: {new Date(method.created_at).toLocaleDateString()}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <span>Updated: {new Date(method.updated_at).toLocaleDateString()}</span>
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex items-center gap-2 ml-4">
                          <Button 
                            variant="outline" 
                            size="sm" 
                            onClick={() => handleEdit(method)}
                          >
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button 
                            variant="outline" 
                            size="sm" 
                            onClick={() => handleDelete(method.id)}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                          <Switch 
                            checked={method.is_active}
                            onCheckedChange={() => handleToggleActive(method.id, method.is_active)}
                            disabled={loading}
                          />
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </div>
            
            {/* Create/Edit Form */}
            {formData.id === null && (
              <div className="mt-8">
                <h3 className="text-xl font-semibold mb-4">Add New Payment Method</h3>
                <form onSubmit={handleMethodSubmit} className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium mb-2">Name</label>
                        <Input 
                          name="name" 
                          value={formData.name} 
                          onChange={handleInputChange} 
                          placeholder="Payment method name" 
                          required
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium mb-2">Provider</label>
                        <Select 
                          value={formData.provider} 
                          onValueChange={(value) => handleSelectChange('provider', value as PaymentProvider)}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select provider" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="stripe">Stripe</SelectItem>
                            <SelectItem value="paypal">PayPal</SelectItem>
                            <SelectItem value="bank">Bank Transfer</SelectItem>
                            <SelectItem value="credit_card">Credit Card</SelectItem>
                            <SelectItem value="crypto">Cryptocurrency</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <Switch 
                          id="active-switch" 
                          checked={formData.is_active} 
                          onCheckedChange={(checked) => handleSwitchChange('is_active', checked)}
                        />
                        <label htmlFor="active-switch" className="text-sm font-medium">
                          Active
                        </label>
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium mb-2">Configuration (JSON)</label>
                        <Textarea 
                          name="configuration" 
                          value={JSON.stringify(formData.configuration, null, 2)} 
                          onChange={(e) => {
                            try {
                              setFormData(prev => ({ ...prev, configuration: JSON.parse(e.target.value) }))
                            } catch {
                              // Keep previous value if JSON is invalid
                            }
                          }} 
                          placeholder="{\n  \"api_key\": \"your_api_key\",\n  \"webhook_secret\": \"your_secret\"\n}" 
                          rows={8}
                        />
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex gap-4 justify-end">
                    <Button 
                      type="button" 
                      variant="outline" 
                      onClick={() => setFormData(prev => ({ ...prev, id: null }))}
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
                          <PlusCircle className="w-4 h-4 mr-2" />
                          Add Payment Method
                        </>
                      )}
                    </Button>
                  </div>
                </form>
              </div>
            )}
          </TabsContent>

          <TabsContent value="settings" className="space-y-4">
            <h3 className="text-xl font-semibold mb-6">Payment Settings</h3>
            
            {settings && (
              <form onSubmit={handleSettingsSubmit} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Currency</label>
                      <Input 
                        name="currency" 
                        value={settingsFormData.currency} 
                        onChange={handleSettingsInputChange} 
                        placeholder="USD" 
                        maxLength={3}
                        required
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium mb-2">Tax Rate (%)</label>
                      <Input 
                        name="tax_rate" 
                        type="number" 
                        step="0.01" 
                        value={settingsFormData.tax_rate} 
                        onChange={handleSettingsInputChange} 
                        placeholder="0.0" 
                        required
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium mb-2">Default Payment Method</label>
                      <Select 
                        value={settingsFormData.default_payment_method_id?.toString() || ''} 
                        onValueChange={(value) => handleSettingsSelectChange('default_payment_method_id', value)}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select default method" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="">None</SelectItem>
                          {methods.map(method => (
                            <SelectItem key={method.id} value={method.id.toString()}>
                              {method.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Additional Settings (JSON)</label>
                      <Textarea 
                        name="settings" 
                        value={JSON.stringify(settingsFormData.settings, null, 2)} 
                        onChange={(e) => {
                          try {
                            setSettingsFormData(prev => ({ ...prev, settings: JSON.parse(e.target.value) }))
                          } catch {
                            // Keep previous value if JSON is invalid
                          }
                        }} 
                        placeholder="{\n  \"auto_invoice\": true,\n  \"invoice_prefix\": \"INV-\"\n}" 
                        rows={8}
                      />
                    </div>
                  </div>
                </div>
                
                <div className="flex gap-4 justify-end">
                  <Button type="submit" disabled={loading}>
                    {loading ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin mr-2" />
                        Saving...
                      </>
                    ) : (
                      <>
                        <Settings className="w-4 h-4 mr-2" />
                        Update Settings
                      </>
                    )}
                  </Button>
                </div>
              </form>
            )}
          </TabsContent>

          <TabsContent value="transactions" className="space-y-4">
            <h3 className="text-xl font-semibold mb-6">Recent Transactions</h3>
            
            {stats && stats.recent_transactions.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-muted-foreground">No recent transactions found</p>
              </div>
            ) : (
              <div className="space-y-4">
                {stats?.recent_transactions.map((transaction: any) => (
                  <Card key={transaction.id} className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <Badge variant={transaction.status === 'COMPLETED' ? 'success' : 'secondary'}>
                            {transaction.status}
                          </Badge>
                          <Badge variant="outline">
                            {transaction.transaction_type}
                          </Badge>
                        </div>
                        
                        <div className="flex items-center gap-4 mb-2">
                          <div className="font-semibold">
                            ${transaction.amount.toFixed(2)} {transaction.currency}
                          </div>
                          <div className="text-muted-foreground">
                            via {transaction.method.name}
                          </div>
                        </div>
                        
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <User className="w-3 h-3" />
                          <span>{transaction.user.name} ({transaction.user.email})</span>
                        </div>
                        
                        <div className="text-sm text-muted-foreground mt-2">
                          {new Date(transaction.created_at).toLocaleString()}
                        </div>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="statistics" className="space-y-4">
            {stats && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* Active Methods Card */}
                <Card className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold">Active Methods</h3>
                      <p className="text-3xl font-bold mt-2">{stats.active_methods}</p>
                    </div>
                    <CheckCircle className="w-8 h-8 text-green-500" />
                  </div>
                </Card>

                {/* Inactive Methods Card */}
                <Card className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold">Inactive Methods</h3>
                      <p className="text-3xl font-bold mt-2">{stats.inactive_methods}</p>
                    </div>
                    <XCircle className="w-8 h-8 text-gray-500" />
                  </div>
                </Card>

                {/* Total Revenue Card */}
                <Card className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold">Total Revenue</h3>
                      <p className="text-3xl font-bold mt-2">${stats.total_revenue.toLocaleString()}</p>
                    </div>
                    <DollarSign className="w-8 h-8 text-green-500" />
                  </div>
                </Card>

                {/* Total Transactions Card */}
                <Card className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold">Total Transactions</h3>
                      <p className="text-3xl font-bold mt-2">{stats.total_transactions}</p>
                    </div>
                    <CreditCard className="w-8 h-8 text-blue-500" />
                  </div>
                </Card>

                {/* Methods by Provider */}
                <Card className="p-6 md:col-span-2">
                  <h3 className="text-lg font-semibold mb-4">Methods by Provider</h3>
                  <div className="space-y-3">
                    {Object.entries(stats.by_provider).filter(([_, count]) => count > 0).map(([provider, count]) => (
                      <div key={provider} className="flex items-center justify-between p-3 bg-secondary rounded-lg">
                        <div className="flex items-center gap-3">
                          <Badge variant="outline">
                            {provider.toUpperCase()}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-4">
                          <span className="text-muted-foreground">{count} method(s)</span>
                          <div className="w-24 h-2 bg-primary rounded-full">
                            <div 
                              className="h-full bg-primary-foreground rounded-full"
                              style={{ width: `${(count / Object.values(stats.by_provider).reduce((a, b) => a + b, 0)) * 100}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>

                {/* Recent Transactions */}
                <Card className="p-6">
                  <h3 className="text-lg font-semibold mb-4">Recent Transactions</h3>
                  <div className="space-y-4">
                    {stats.recent_transactions.slice(0, 3).map((transaction: any) => (
                      <div key={transaction.id} className="flex items-center gap-3 p-3 bg-secondary rounded-lg">
                        <div className="flex-1">
                          <div className="font-medium">${transaction.amount.toFixed(2)} {transaction.currency}</div>
                          <div className="text-sm text-muted-foreground">{transaction.user.name}</div>
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {new Date(transaction.created_at).toLocaleDateString()}
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