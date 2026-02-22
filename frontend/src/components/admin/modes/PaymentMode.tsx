import { useState, useEffect } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../ui/tabs'
import { Card } from '../../ui/card'
import { Alert, AlertDescription } from '../../ui/alert'
import { 
  Settings, 
  AlertCircle, 
  Loader2, 
  PlusCircle, 
  List,
  CreditCard,
  DollarSign,
  BarChart2,
  Search,
  Edit,
  Trash2,
  CheckCircle,
  XCircle,
  Globe
} from 'lucide-react'
import { Progress } from '../../ui/progress'
import { Button } from '../../ui/button'
import { Input } from '../../ui/input'
import { Textarea } from '../../ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../ui/select'
import { Switch } from '../../ui/switch'
import { Badge } from '../../ui/badge'
import { toast } from 'react-hot-toast'
import { PaymentProvider } from '../../../types/payment'
import type {
  PaymentMethod,
  PaymentSettings,
  PaymentTransaction,
  PaymentStats,
  UserBalanceSummary,
  UserBalanceUserListItem,
} from '../../../types/payment'
import {
  getPaymentMethods,
  getPaymentSettings,
  getPaymentStats,
  getPaymentTransactions,
  createPaymentMethod,
  updatePaymentMethod,
  deletePaymentMethod,
  updatePaymentSettings,
  adjustUserBalance,
  getBalanceUsers,
  getUserBalanceSummary,
} from '../../../services/paymentService'

// Tab type definition
type TabValue = 'methods' | 'settings' | 'transactions' | 'statistics' | 'balances'

export const PaymentMode = () => {
  const [activeTab, setActiveTab] = useState<TabValue>('methods')
  const [methods, setMethods] = useState<PaymentMethod[]>([])
  const [settings, setSettings] = useState<PaymentSettings | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [stats, setStats] = useState<PaymentStats | null>(null)
  const [transactions, setTransactions] = useState<PaymentTransaction[]>([])
  const [balanceUsers, setBalanceUsers] = useState<UserBalanceUserListItem[]>([])
  const [balanceSearch, setBalanceSearch] = useState('')
  const [selectedBalanceUserId, setSelectedBalanceUserId] = useState<number | null>(null)
  const [balanceSummary, setBalanceSummary] = useState<UserBalanceSummary | null>(null)
  const [balanceForm, setBalanceForm] = useState({
    currency: 'USD',
    amount_delta: 0,
    reason: '',
  })


  // Form state for creating/editing payment methods
  const [formData, setFormData] = useState({
    id: null as number | null,
    name: '',
    provider: PaymentProvider.STRIPE,
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
    loadTransactions()
    loadBalanceUsers()
  }, [])

  const loadMethods = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await getPaymentMethods()
      setMethods(response.items)
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load payment methods')
      console.error('Error loading payment methods:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadSettings = async () => {
    try {
      const response = await getPaymentSettings()
      setSettings(response)
      setSettingsFormData({
        currency: response.currency,
        tax_rate: response.tax_rate || 0.0,
        default_payment_method_id: response.default_payment_method_id ?? null,
        settings: response.settings || {}
      })
      
    } catch (err) {
      console.error('Error loading payment settings:', err)
    }
  }

  const loadStatistics = async () => {
    try {
      const response = await getPaymentStats()
      setStats(response)
      
    } catch (err) {
      console.error('Error loading statistics:', err)
    }
  }

  const loadTransactions = async () => {
    try {
      const response = await getPaymentTransactions()
      setTransactions(response.items)
      
    } catch (err) {
      console.error('Error loading transactions:', err)
    }
  }

  const loadBalanceUsers = async (search?: string) => {
    try {
      const response = await getBalanceUsers(search)
      setBalanceUsers(response.items)
      if (!selectedBalanceUserId && response.items.length > 0) {
        const first = response.items[0]
        setSelectedBalanceUserId(first.user_id)
        await loadBalanceSummary(first.user_id)
      } else if (selectedBalanceUserId) {
        await loadBalanceSummary(selectedBalanceUserId)
      }
    } catch (err) {
      console.error('Error loading balance users:', err)
    }
  }

  const loadBalanceSummary = async (userId: number) => {
    try {
      const summary = await getUserBalanceSummary(userId)
      setBalanceSummary(summary)
    } catch (err) {
      console.error('Error loading balance summary:', err)
      setBalanceSummary(null)
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
    setSettingsFormData(prev => ({
      ...prev,
      [name]:
        name === 'default_payment_method_id'
          ? (value ? parseInt(value, 10) : null)
          : value,
    }))
  }

  const handleSwitchChange = (name: string, checked: boolean) => {
    setFormData(prev => ({ ...prev, [name]: checked }))
  }

  const handleMethodSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      setLoading(true)
      
      if (formData.id) {
        // Update existing
        await updatePaymentMethod(formData.id, {
          name: formData.name,
          is_active: formData.is_active,
          configuration: formData.configuration
        })
        toast.success("Payment method has been successfully updated.")
        await loadMethods()
      } else {
        // Create new
        await createPaymentMethod({
          name: formData.name,
          provider: formData.provider,
          is_active: formData.is_active,
          configuration: formData.configuration
        })
        
        toast.success("New payment method has been successfully created.")
        
        // Reset form
        setFormData({
          id: null,
          name: '',
          provider: PaymentProvider.STRIPE,
          is_active: true,
          configuration: {}
        })
        await loadMethods()
      }
      
      setActiveTab('methods')
      
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to save payment method')
      console.error('Error saving payment method:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSettingsSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      setLoading(true)
      
      const updatedSettings = await updatePaymentSettings({
        currency: settingsFormData.currency,
        tax_rate: settingsFormData.tax_rate,
        default_payment_method_id: settingsFormData.default_payment_method_id ?? undefined,
        settings: settingsFormData.settings
      })
      
      setSettings(updatedSettings)
      
      toast.success("Payment settings have been successfully updated.")
      
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to update settings')
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
      configuration: method.configuration || {}
    })
    setActiveTab('methods')
  }

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this payment method?')) {
      try {
        setLoading(true)
        await deletePaymentMethod(id)
        await loadMethods()
        
        toast.success("Payment method has been successfully deleted.")
        
      } catch (err) {
        toast.error(err instanceof Error ? err.message : 'Failed to delete payment method')
        console.error('Error deleting payment method:', err)
      } finally {
        setLoading(false)
      }
    }
  }

  const handleToggleActive = async (id: number, currentStatus: boolean) => {
    try {
      setLoading(true)
      const method = methods.find(m => m.id === id)
      if (method) {
        await updatePaymentMethod(id, { is_active: !currentStatus })
        await loadMethods()
        
        toast.success(`Payment method has been ${!currentStatus ? 'activated' : 'deactivated'}.`)
      }
      
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to update status')
      console.error('Error updating status:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleBalanceSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    await loadBalanceUsers(balanceSearch.trim() || undefined)
  }

  const handleAdjustBalance = async (direction: 'add' | 'deduct') => {
    if (!selectedBalanceUserId) {
      toast.error('Select a user to adjust balance')
      return
    }
    if (!balanceForm.reason.trim()) {
      toast.error('Reason is required')
      return
    }
    if (!balanceForm.amount_delta || Number.isNaN(balanceForm.amount_delta)) {
      toast.error('Amount must be greater than zero')
      return
    }

    const amount = Math.abs(balanceForm.amount_delta)
    try {
      setLoading(true)
      const summary = await adjustUserBalance(selectedBalanceUserId, {
        currency: balanceForm.currency.toUpperCase(),
        amount_delta: direction === 'add' ? amount : -amount,
        reason: balanceForm.reason.trim(),
      })
      setBalanceSummary(summary)
      toast.success(`Balance ${direction === 'add' ? 'credited' : 'debited'} successfully`)
      setBalanceForm((previous) => ({ ...previous, amount_delta: 0, reason: '' }))
      await loadBalanceUsers(balanceSearch.trim() || undefined)
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to adjust balance')
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
              <span className="font-medium">{typeof stats.total_revenue === 'number' ? stats.total_revenue.toLocaleString() : '0'}</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
              <Globe className="w-4 h-4" />
              <span className="font-medium">{Object.values(stats.by_provider).reduce((a: number, b: any) => a + (typeof b === 'number' ? b : 0), 0)} Gateways</span>
            </div>
          </div>
        )}
      </div>

      {/* Main Content Tabs */}
      <Card className="p-6">
        <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as TabValue)}>
          <TabsList className="grid w-full grid-cols-5 mb-6">
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
            <TabsTrigger value="balances" className="flex items-center gap-2">
              <DollarSign className="w-4 h-4" />
              Balances
            </TabsTrigger>
          </TabsList>

          <TabsContent value="methods" className="space-y-4">
            <div className="flex justify-end mb-4">
              <Button onClick={() => {
                setFormData({
                  id: null,
                  name: '',
                  provider: PaymentProvider.STRIPE,
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
                              {Object.entries(method.configuration || {}).map(([key, value]) => (
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
                          placeholder='{"api_key": "your_api_key", "webhook_secret": "your_secret"}'
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
                        value={settingsFormData.default_payment_method_id?.toString() || '__none__'} 
                        onValueChange={(value) =>
                          handleSettingsSelectChange(
                            'default_payment_method_id',
                            value === '__none__' ? '' : value,
                          )
                        }
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select default method" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="__none__">None</SelectItem>
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
                        placeholder='{"auto_invoice": true, "invoice_prefix": "INV-"}'
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
            
            {transactions.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-muted-foreground">No recent transactions found</p>
              </div>
            ) : (
              <div className="space-y-4">
                {transactions.map((transaction: any) => (
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
                            via {methods.find(m => m.id === transaction.payment_method_id)?.name || 'Unknown'}
                          </div>
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

                {/* Methods by Provider */}
                <Card className="p-6 md:col-span-2">
                  <h3 className="text-lg font-semibold mb-4">Methods by Provider</h3>
                  <div className="space-y-3">
                    {Object.entries(stats.by_provider).filter(([_, count]) => typeof count === 'number' && count > 0).map(([provider, count]) => {
                      const safeCount = typeof count === 'number' ? count : 0;
                      return (
                        <div key={provider} className="flex items-center justify-between p-3 bg-secondary rounded-lg">
                          <div className="flex items-center gap-3">
                            <Badge variant="outline">
                              {provider.toUpperCase()}
                            </Badge>
                          </div>
                          <div className="flex items-center gap-4">
                            <span className="text-muted-foreground">{safeCount} method(s)</span>
                            <div className="w-24">
                              <Progress 
                                value={(safeCount / Object.values(stats.by_provider).reduce((a: number, b: any) => a + (typeof b === 'number' ? b : 0), 0)) * 100}
                                indicatorClassName="bg-primary-foreground"
                                className="bg-primary h-2"
                              />
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </Card>

                {/* Recent Transactions */}
                <Card className="p-6">
                  <h3 className="text-lg font-semibold mb-4">Recent Transactions</h3>
                  <div className="space-y-4">
                    {transactions.slice(0, 3).map((transaction: any) => (
                      <div key={transaction.id} className="flex items-center gap-3 p-3 bg-secondary rounded-lg">
                        <div className="flex-1">
                          <div className="font-medium">${transaction.amount.toFixed(2)} {transaction.currency}</div>
                          <div className="text-sm text-muted-foreground">{new Date(transaction.created_at).toLocaleDateString()}</div>
                        </div>
                        <Badge variant={transaction.status === 'COMPLETED' ? 'success' : 'secondary'}>
                          {transaction.status}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </Card>
              </div>
            )}
          </TabsContent>

          <TabsContent value="balances" className="space-y-4">
            <h3 className="text-xl font-semibold">User Balances</h3>
            <p className="text-sm text-muted-foreground">
              Add or deduct wallet balances per user in any currency.
            </p>

            <Card className="p-4">
              <form className="flex flex-wrap items-center gap-3" onSubmit={handleBalanceSearch}>
                <div className="relative flex-1 min-w-[240px]">
                  <Search className="pointer-events-none absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    value={balanceSearch}
                    onChange={(event) => setBalanceSearch(event.target.value)}
                    placeholder="Search by username or email..."
                    className="pl-9"
                  />
                </div>
                <Button type="submit" variant="outline">
                  Search
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setBalanceSearch('')
                    void loadBalanceUsers()
                  }}
                >
                  Reset
                </Button>
              </form>
            </Card>

            <div className="grid grid-cols-1 gap-4 xl:grid-cols-[320px_1fr]">
              <Card className="max-h-[560px] overflow-auto p-3">
                <div className="space-y-2">
                  {balanceUsers.length === 0 ? (
                    <p className="p-3 text-sm text-muted-foreground">No users found.</p>
                  ) : (
                    balanceUsers.map((item) => (
                      <button
                        key={item.user_id}
                        type="button"
                        className={`w-full rounded-md border p-3 text-left transition ${
                          selectedBalanceUserId === item.user_id
                            ? 'border-primary bg-primary/10'
                            : 'border-border hover:bg-accent'
                        }`}
                        onClick={() => {
                          setSelectedBalanceUserId(item.user_id)
                          void loadBalanceSummary(item.user_id)
                        }}
                      >
                        <p className="font-medium">{item.username}</p>
                        <p className="text-xs text-muted-foreground">{item.email}</p>
                      </button>
                    ))
                  )}
                </div>
              </Card>

              <Card className="space-y-4 p-4">
                {!selectedBalanceUserId || !balanceSummary ? (
                  <p className="text-sm text-muted-foreground">Select a user to view balances.</p>
                ) : (
                  <>
                    <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
                      {balanceSummary.balances.length === 0 ? (
                        <div className="rounded-md border border-border p-4 text-sm text-muted-foreground">
                          No balances yet.
                        </div>
                      ) : (
                        balanceSummary.balances.map((balance) => (
                          <div key={balance.id} className="rounded-md border border-border p-4">
                            <p className="text-xs uppercase tracking-wide text-muted-foreground">{balance.currency}</p>
                            <p className="mt-2 text-2xl font-semibold">{balance.balance.toFixed(2)}</p>
                          </div>
                        ))
                      )}
                    </div>

                    <div className="rounded-md border border-border p-4">
                      <h4 className="text-base font-semibold">Adjust Balance</h4>
                      <div className="mt-3 grid grid-cols-1 gap-3 md:grid-cols-3">
                        <Input
                          value={balanceForm.currency}
                          onChange={(event) => setBalanceForm((prev) => ({ ...prev, currency: event.target.value.toUpperCase() }))}
                          placeholder="Currency (USD)"
                          maxLength={3}
                        />
                        <Input
                          type="number"
                          step="0.01"
                          value={balanceForm.amount_delta}
                          onChange={(event) =>
                            setBalanceForm((prev) => ({ ...prev, amount_delta: Number(event.target.value) }))
                          }
                          placeholder="Amount"
                        />
                        <Input
                          value={balanceForm.reason}
                          onChange={(event) => setBalanceForm((prev) => ({ ...prev, reason: event.target.value }))}
                          placeholder="Reason"
                        />
                      </div>
                      <div className="mt-3 flex flex-wrap gap-2">
                        <Button
                          type="button"
                          onClick={() => void handleAdjustBalance('add')}
                          disabled={loading}
                        >
                          Credit
                        </Button>
                        <Button
                          type="button"
                          variant="destructive"
                          onClick={() => void handleAdjustBalance('deduct')}
                          disabled={loading}
                        >
                          Debit
                        </Button>
                      </div>
                    </div>

                    <div className="rounded-md border border-border p-4">
                      <h4 className="text-base font-semibold">Recent Balance Transactions</h4>
                      <div className="mt-3 space-y-2">
                        {balanceSummary.transactions.length === 0 ? (
                          <p className="text-sm text-muted-foreground">No balance transactions yet.</p>
                        ) : (
                          balanceSummary.transactions.slice(0, 20).map((tx) => (
                            <div key={tx.id} className="flex items-center justify-between rounded-md bg-secondary p-3">
                              <div>
                                <p className="text-sm font-medium">{tx.reason}</p>
                                <p className="text-xs text-muted-foreground">
                                  {new Date(tx.created_at).toLocaleString()}
                                </p>
                              </div>
                              <div className="text-right">
                                <p className={`text-sm font-semibold ${tx.amount_delta >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                                  {tx.amount_delta >= 0 ? '+' : ''}
                                  {tx.amount_delta.toFixed(2)} {tx.currency}
                                </p>
                              </div>
                            </div>
                          ))
                        )}
                      </div>
                    </div>
                  </>
                )}
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </Card>
    </div>
  )
}
