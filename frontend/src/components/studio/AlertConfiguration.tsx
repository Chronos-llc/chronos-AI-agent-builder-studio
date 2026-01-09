import React, { useState, useEffect } from 'react';
import {
  AlertRule,
  AlertRuleCreate,
  AlertRuleUpdate,
  AlertHistory,
  AlertSeverity,
  AlertCondition,
  MetricType,
} from '../../types/systemOptimization';
import {
  listAlerts,
  createAlert,
  updateAlert,
  deleteAlert,
  getAlertHistory,
  acknowledgeAlert,
} from '../../services/systemOptimizationService';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Badge } from '../ui/badge';
import { ScrollArea } from '../ui/scroll-area';
import { Input } from '../ui/input';
import {
  Bell,
  BellOff,
  Plus,
  Trash2,
  Edit,
  CheckCircle,
  Clock,
  AlertTriangle,
  History,
  Volume2,
  Settings,
  RefreshCw,
} from 'lucide-react';
import toast from 'react-hot-toast';

interface AlertConfigurationProps {
  agentId?: number;
}

export function AlertConfiguration({ agentId }: AlertConfigurationProps) {
  const [alerts, setAlerts] = useState<AlertRule[]>([]);
  const [alertHistory, setAlertHistory] = useState<Record<number, AlertHistory[]>>({});  
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingAlert, setEditingAlert] = useState<AlertRule | null>(null);
  const [selectedAlert, setSelectedAlert] = useState<AlertRule | null>(null);

  // Form state
  const [formData, setFormData] = useState<AlertRuleCreate>({
    name: '',
    description: '',
    metric_type: 'CPU',
    condition: 'GT',
    threshold_value: 80,
    severity: 'MEDIUM',
    is_active: true,
    cooldown_period: 300,
  });

  const fetchAlerts = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await listAlerts();
      setAlerts(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load alerts');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlertHistory = async (alertId: number) => {
    try {
      const history = await getAlertHistory(alertId);
      setAlertHistory((prev) => ({ ...prev, [alertId]: history }));
    } catch (err) {
      console.error('Failed to fetch alert history:', err);
    }
  };

  const handleCreateAlert = async () => {
    if (!formData.name || !formData.metric_type) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      await createAlert(formData);
      toast.success('Alert rule created');
      setShowCreateForm(false);
      setFormData({
        name: '',
        description: '',
        metric_type: 'CPU',
        condition: 'GT',
        threshold_value: 80,
        severity: 'MEDIUM',
        is_active: true,
        cooldown_period: 300,
      });
      fetchAlerts();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to create alert');
    }
  };

  const handleUpdateAlert = async () => {
    if (!editingAlert) return;

    try {
      const updateData: AlertRuleUpdate = {
        name: formData.nam,
        description: formData.description,
        metric_type: formData.metric_type,
        condition: formData.condition,
        threshold_value: formData.threshold_value,
        severity: formData.severity,
        is_active: formData.is_active,
        cooldown_period: formData.cooldown_period,
      };

      await updateAlert(editingAlert.id, updateData);
      toast.success('Alert rule updated');
      setEditingAlert(null);
      setFormData({
        name: '',
        description: '',
        metric_type: 'CPU',
        condition: 'GT',
        threshold_value: 80,
        severity: 'MEDIUM',
        is_active: true,
        cooldown_period: 300,
      });
      fetchAlerts();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to update alert');
    }
  };

  const handleDeleteAlert = async (alertId: number) => {
    if (!confirm('Are you sure you want to delete this alert rule?')) return;

    try {
      await deleteAlert(alertId);
      toast.success('Alert rule deleted');
      fetchAlerts();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to delete alert');
    }
  };

  const handleToggleActive = async (alert: AlertRule) => {
    try {
      await updateAlert(alert.id, { is_active: !alert.is_active });
      toast.success(`Alert ${alert.is_active ? 'disabled' : 'enabled'}`);
      fetchAlerts();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to toggle alert');
    }
  };

  const handleAcknowledge = async (alertId: number) => {
    try {
      await acknowledgeAlert(alertId);
      toast.success('Alert acknowledged');
      if (selectedAlert) {
        fetchAlertHistory(selectedAlert.id);
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to acknowledge alert');
    }
  };

  const startEdit = (alert: AlertRule) => {
    setEditingAlert(alert);
    setFormData({
      name: alert.name,
      description: alert.description || '',
      metric_type: alert.metric_type,
      condition: alert.condition,
      threshold_value: alert.threshold_value,
      severity: alert.severity,
      is_active: alert.is_active,
      cooldown_period: alert.cooldown_period,
    });
  };

  const getSeverityConfig = (severity: AlertSeverity) => {
    const configs = {
      LOW: { color: 'bg-blue-500', text: 'text-blue-400', border: 'border-blue-500' },
      MEDIUM: { color: 'bg-yellow-500', text: 'text-yellow-400', border: 'border-yellow-500' },
      HIGH: { color: 'bg-orange-500', text: 'text-orange-400', border: 'border-orange-500' },
      CRITICAL: { color: 'bg-red-500', text: 'text-red-400', border: 'border-red-500' },
    };
    return configs[severity];
  };

  const getConditionLabel = (condition: AlertCondition, threshold: number) => {
    const labels = {
      GT: `> ${threshold}`,
      LT: `< ${threshold}`,
      EQ: `= ${threshold}`,
      GTE: `>= ${threshold}`,
      LTE: `<= ${threshold}`,
    };
    return labels[condition];
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-500" />
          <p className="text-gray-400">Loading alert rules...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center text-red-500">
          <p>{error}</p>
          <Button onClick={fetchAlerts} className="mt-4" variant="outline">
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bell className="w-5 h-5 text-yellow-500" />
          <h2 className="text-xl font-bold">Alert Configuration</h2>
        </div>
        <Button onClick={() => setShowCreateForm(true)} variant="outline" size="sm">
          <Plus className="w-4 h-4 mr-2" />
          Create Alert Rule
        </Button>
      </div>

      {/* Create/Edit Form */}
      {(showCreateForm || editingAlert) && (
        <Card className="border-yellow-500/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="w-4 h-4" />
              {editingAlert ? 'Edit Alert Rule' : 'Create Alert Rule'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-gray-400 block mb-1">Name *</label>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="Alert name"
                  className="bg-gray-800"
                />
              </div>

              <div>
                <label className="text-sm text-gray-400 block mb-1">Description</label>
                <Input
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Optional description"
                  className="bg-gray-800"
                />
              </div>

              <div>
                <label className="text-sm text-gray-400 block mb-1">Metric Type *</label>
                <Select
                  value={formData.metric_type}
                  onValueChange={(v) => setFormData({ ...formData, metric_type: v as MetricType })}
                >
                  <SelectTrigger className="bg-gray-800">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-gray-800">
                    <SelectItem value="CPU">CPU</SelectItem>
                    <SelectItem value="MEMORY">Memory</SelectItem>
                    <SelectItem value="DISK">Disk</SelectItem>
                    <SelectItem value="NETWORK">Network</SelectItem>
                    <SelectItem value="RESPONSE_TIME">Response Time</SelectItem>
                    <SelectItem value="THROUGHPUT">Throughput</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm text-gray-400 block mb-1">Condition *</label>
                <div className="flex gap-2">
                  <Select
                    value={formData.condition}
                    onValueChange={(v) => setFormData({ ...formData, condition: v as AlertCondition })}
                  >
                    <SelectTrigger className="bg-gray-800 w-24">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-gray-800">
                      <SelectItem value="GT">{'>'} (Greater)</SelectItem>
                      <SelectItem value="LT">{'<'} (Less)</SelectItem>
                      <SelectItem value="EQ">= (Equal)</SelectItem>
                      <SelectItem value="GTE">{'>= '} (Greater or Equal)</SelectItem>
                      <SelectItem value="LTE">{'<='} (Less or Equal)</SelectItem>
                    </SelectContent>
                  </Select>
                  <Input
                    type="number"
                    value={formData.threshold_value}
                    onChange={(e) => setFormData({ ...formData, threshold_value: parseFloat(e.target.value) })}
                    className="bg-gray-800 flex-1"
                  />
                </div>
              </div>

              <div>
                <label className="text-sm text-gray-400 block mb-1">Severity *</label>
                <Select
                  value={formData.severity}
                  onValueChange={(v) => setFormData({ ...formData, severity: v as AlertSeverity })}
                >
                  <SelectTrigger className="bg-gray-800">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-gray-800">
                    <SelectItem value="LOW">Low</SelectItem>
                    <SelectItem value="MEDIUM">Medium</SelectItem>
                    <SelectItem value="HIGH">High</SelectItem>
                    <SelectItem value="CRITICAL">Critical</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm text-gray-400 block mb-1">Cooldown (seconds)</label>
                <Input
                  type="number"
                  value={formData.cooldown_period}
                  onChange={(e) => setFormData({ ...formData, cooldown_period: parseInt(e.target.value) })}
                  className="bg-gray-800"
                />
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={formData.is_active}
                  onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  className="rounded"
                />
                <label htmlFor="is_active" className="text-sm">
                  Active
                </label>
              </div>
            </div>

            <div className="flex gap-2 mt-6">
              <Button
                onClick={editingAlert ? handleUpdateAlert : handleCreateAlert}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {editingAlert ? 'Update Alert' : 'Create Alert'}
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setShowCreateForm(false);
                  setEditingAlert(null);
                  setFormData({
                    name: '',
                    description: '',
                    metric_type: 'CPU',
                    condition: 'GT',
                    threshold_value: 80,
                    severity: 'MEDIUM',
                    is_active: true,
                    cooldown_period: 300,
                  });
                }}
              >
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Alert Rules List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Alert Rules */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="w-4 h-4" />
              Alert Rules ({alerts.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-96">
              {alerts.length === 0 ? (
                <div className="text-center py-8 text-gray-400">
                  <BellOff className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>No alert rules configured</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {alerts.map((alert) => {
                    const severityConfig = getSeverityConfig(alert.severity);
                    return (
                      <div
                        key={alert.id}
                        className={`p-4 border border-gray-700 rounded-lg bg-gray-800/50 hover:bg-gray-800 transition-colors ${
                          !alert.is_active ? 'opacity-50' : ''
                        }`}
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <Volume2 className={`w-4 h-4 ${alert.is_active ? 'text-green-500' : 'text-gray-500'}`} />
                            <span className="font-medium">{alert.name}</span>
                          </div>
                          <Badge className={`${severityConfig.color} text-white`}>
                            {alert.severity}
                          </Badge>
                        </div>

                        <div className="text-sm text-gray-400 mb-2">
                          {alert.metric_type} {getConditionLabel(alert.condition, alert.threshold_value)}
                        </div>

                        {alert.description && (
                          <p className="text-xs text-gray-500 mb-2">{alert.description}</p>
                        )}

                        <div className="flex items-center gap-4 text-xs text-gray-500">
                          <span>Cooldown: {alert.cooldown_period}s</span>
                          <span>Created: {new Date(alert.created_at).toLocaleDateString()}</span>
                        </div>

                        <div className="flex gap-2 mt-3">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => startEdit(alert)}
                          >
                            <Edit className="w-3 h-3 mr-1" />
                            Edit
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleToggleActive(alert)}
                          >
                            {alert.is_active ? (
                              <>
                                <BellOff className="w-3 h-3 mr-1" />
                                Disable
                              </>
                            ) : (
                              <>
                                <Bell className="w-3 h-3 mr-1" />
                                Enable
                              </>
                            )}
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setSelectedAlert(alert);
                              fetchAlertHistory(alert.id);
                            }}
                          >
                            <History className="w-3 h-3 mr-1" />
                            History
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDeleteAlert(alert.id)}
                            className="text-red-400 hover:text-red-300"
                          >
                            <Trash2 className="w-3 h-3 mr-1" />
                            Delete
                          </Button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </ScrollArea>
          </CardContent>
        </Card>

        {/* Alert History */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <History className="w-4 h-4" />
              Alert History
              {selectedAlert && (
                <span className="text-sm font-normal text-gray-400">
                  - {selectedAlert.name}
                </span>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {!selectedAlert ? (
              <div className="text-center py-8 text-gray-400">
                <Clock className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>Select an alert rule to view history</p>
              </div>
            ) : (
              <ScrollArea className="h-96">
                {alertHistory[selectedAlert.id]?.length === 0 ? (
                  <div className="text-center py-8 text-gray-400">
                    <CheckCircle className="w-12 h-12 mx-auto mb-4 text-green-500" />
                    <p>No alert history</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {alertHistory[selectedAlert.id]?.map((history, index) => (
                      <div
                        key={index}
                        className={`p-3 border rounded-lg ${
                          history.acknowledged
                            ? 'border-gray-700 bg-gray-800/30'
                            : 'border-yellow-500/50 bg-yellow-500/10'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm font-medium">
                            Triggered: {history.triggered_value}
                          </span>
                          <Badge
                            className={history.acknowledged ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'}
                          >
                            {history.acknowledged ? 'Acknowledged' : 'Pending'}
                          </Badge>
                        </div>
                        <div className="text-xs text-gray-400">
                          {new Date(history.triggered_at).toLocaleString()}
                        </div>
                        {history.acknowledged && history.acknowledged_by && (
                          <div className="text-xs text-gray-500 mt-1">
                            Acknowledged by {history.acknowledged_by}
                          </div>
                        )}
                        {!history.acknowledged && (
                          <Button
                            size="sm"
                            variant="outline"
                            className="mt-2"
                            onClick={() => handleAcknowledge(selectedAlert.id)}
                          >
                            <CheckCircle className="w-3 h-3 mr-1" />
                            Acknowledge
                          </Button>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </ScrollArea>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default AlertConfiguration;