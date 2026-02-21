import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ProtectedRoute } from '../components/ProtectedRoute';
import { useAuth } from '../contexts/AuthContext';
import { PlatformLoadingScreen } from '../components/loading/PlatformLoadingScreen';

interface IntegrationConfig {
  id: number;
  integration_id: number;
  config: any;
  credentials: any;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface Integration {
  id: number;
  name: string;
  description: string;
  integration_type: string;
  category: string;
  icon: string;
  config_schema: any;
  credentials_schema: any;
}

const IntegrationConfigurationPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [integration, setIntegration] = useState<Integration | null>(null);
  const [config, setConfig] = useState<IntegrationConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'settings' | 'credentials' | 'advanced'>('settings');
  const [formData, setFormData] = useState<Record<string, any>>({});
  const [credentialData, setCredentialData] = useState<Record<string, any>>({});
  const [isSaving, setIsSaving] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);

  useEffect(() => {
    if (id) {
      fetchIntegrationDetails(parseInt(id));
      fetchIntegrationConfig(parseInt(id));
    }
  }, [id]);

  const fetchIntegrationDetails = async (integrationId: number) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`/api/v1/integrations/${integrationId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch integration details');
      }

      const data = await response.json();
      setIntegration(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch integration details');
    } finally {
      setLoading(false);
    }
  };

  const fetchIntegrationConfig = async (integrationId: number) => {
    try {
      setLoading(true);
      setError(null);

      // In a real implementation, this would fetch the existing config
      // For now, we'll use mock data
      const mockConfig = {
        id: 1,
        integration_id: integrationId,
        config: {
          timeout: 30,
          retry_attempts: 3,
          enable_logging: true,
          cache_responses: false
        },
        credentials: {
          api_key: '********',
          secret_key: '********'
        },
        is_active: true,
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-01T00:00:00Z'
      };
      
      setConfig(mockConfig);
      setFormData(mockConfig.config);
      setCredentialData(mockConfig.credentials);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch integration config');
    } finally {
      setLoading(false);
    }
  };

  const handleConfigChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const checked = (e.target as HTMLInputElement).checked;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleCredentialChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setCredentialData({
      ...credentialData,
      [name]: value
    });
  };

  const handleSave = async () => {
    if (!integration || !config || !id) return;

    setIsSaving(true);
    setError(null);

    try {
      const response = await fetch(`/api/v1/integrations/config/${config.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          config: formData,
          credentials: credentialData,
          is_active: true
        })
      });

      if (!response.ok) {
        throw new Error('Failed to save configuration');
      }

      const updatedConfig = await response.json();
      setConfig(updatedConfig);
      setIsSaving(false);
      
      // Show success message
      setTestResult({
        success: true,
        message: 'Configuration saved successfully!'
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save configuration');
      setIsSaving(false);
    }
  };

  const handleTestConnection = async () => {
    if (!integration || !id) return;

    setIsTesting(true);
    setTestResult(null);

    try {
      // Simulate connection test
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Mock test result
      const success = Math.random() > 0.2; // 80% chance of success for demo
      
      if (success) {
        setTestResult({
          success: true,
          message: 'Connection test successful! All systems are operational.'
        });
      } else {
        setTestResult({
          success: false,
          message: 'Connection test failed. Please check your credentials and configuration.'
        });
      }
    } catch (err) {
      setTestResult({
        success: false,
        message: err instanceof Error ? err.message : 'Connection test failed'
      });
    } finally {
      setIsTesting(false);
    }
  };

  const renderFormField = (name: string, label: string, type: string = 'text', options: string[] = []) => {
    return (
      <div key={name} className="mb-4">
        <label htmlFor={name} className="block text-sm font-medium text-muted-foreground mb-1">
          {label}
        </label>
        {type === 'select' ? (
          <select
            id={name}
            name={name}
            value={formData[name] || ''}
            onChange={handleConfigChange}
            className="w-full px-3 py-2 border border-border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {options.map((option) => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        ) : type === 'checkbox' ? (
          <div className="flex items-center">
            <input
              type="checkbox"
              id={name}
              name={name}
              checked={formData[name] || false}
              onChange={handleConfigChange}
              className="h-4 w-4 text-cyan-300 border-border rounded focus:ring-blue-500"
            />
          </div>
        ) : (
          <input
            type={type}
            id={name}
            name={name}
            value={formData[name] || ''}
            onChange={handleConfigChange}
            className="w-full px-3 py-2 border border-border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        )}
      </div>
    );
  };

  const renderCredentialField = (name: string, label: string, type: string = 'password') => {
    return (
      <div key={name} className="mb-4">
        <label htmlFor={name} className="block text-sm font-medium text-muted-foreground mb-1">
          {label}
        </label>
        <input
          type={type}
          id={name}
          name={name}
          value={credentialData[name] || ''}
          onChange={handleCredentialChange}
          className="w-full px-3 py-2 border border-border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder={`Enter ${label.toLowerCase()}`}
        />
      </div>
    );
  };

  if (loading) {
    return (
      <ProtectedRoute>
        <PlatformLoadingScreen />
      </ProtectedRoute>
    );
  }

  if (error) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-background p-6">
          <div className="max-w-4xl mx-auto">
            <div className="bg-rose-500/10 border border-red-200 rounded-lg p-6">
              <p className="text-rose-400 mb-4">⚠️ {error}</p>
              <button
                onClick={() => {
                  if (id) {
                    fetchIntegrationDetails(parseInt(id));
                    fetchIntegrationConfig(parseInt(id));
                  }
                }}
                className="text-sm text-rose-400 hover:text-red-800"
              >
                Try again
              </button>
            </div>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  if (!integration) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-background p-6">
          <div className="max-w-4xl mx-auto">
            <div className="text-center py-12">
              <div className="text-6xl text-gray-300 mb-4">🔍</div>
              <p className="text-muted-foreground mb-2">Integration not found</p>
              <button
                onClick={() => navigate('/app/integrations')}
                className="mt-4 bg-cyan-400 text-white px-4 py-2 rounded-md hover:bg-cyan-300"
              >
                Back to Marketplace
              </button>
            </div>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-background p-6">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="flex justify-between items-center mb-6">
            <div>
              <h1 className="text-3xl font-bold text-foreground">Configure {integration.name}</h1>
              <p className="text-muted-foreground mt-1">Customize integration settings and credentials</p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => navigate(`/app/integrations/${integration.id}`)}
                className="bg-gray-100 text-muted-foreground px-4 py-2 rounded-md hover:bg-gray-200"
              >
                ← Back to Details
              </button>
              <button
                onClick={() => navigate('/app/integrations')}
                className="bg-gray-100 text-muted-foreground px-4 py-2 rounded-md hover:bg-gray-200"
              >
                View All Integrations
              </button>
            </div>
          </div>

          {/* Integration Info */}
          <div className="bg-card rounded-lg shadow-sm p-6 mb-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <span className="text-cyan-300 text-2xl">{integration.icon || '🔌'}</span>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-foreground">{integration.name}</h3>
                <p className="text-muted-foreground">{integration.description}</p>
                <div className="flex gap-2 mt-2">
                  <span className="text-xs bg-green-100 text-emerald-300 px-2 py-1 rounded-full">
                    {integration.category.replace('_', ' ')}
                  </span>
                  <span className="text-xs bg-blue-100 text-cyan-300 px-2 py-1 rounded-full">
                    {integration.integration_type.replace('_', ' ')}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Configuration Tabs */}
          <div className="bg-card rounded-lg shadow-sm overflow-hidden">
            <div className="border-b border-border px-6">
              <div className="flex -mb-px">
                <button
                  onClick={() => setActiveTab('settings')}
                  className={`flex-1 py-4 px-1 text-center border-b-2 font-medium text-sm ${activeTab === 'settings' 
                    ? 'border-blue-600 text-cyan-300'
                    : 'border-transparent text-muted-foreground hover:text-muted-foreground hover:border-border'}`}
                >
                  General Settings
                </button>
                <button
                  onClick={() => setActiveTab('credentials')}
                  className={`flex-1 py-4 px-1 text-center border-b-2 font-medium text-sm ${activeTab === 'credentials'
                    ? 'border-blue-600 text-cyan-300'
                    : 'border-transparent text-muted-foreground hover:text-muted-foreground hover:border-border'}`}
                >
                  Credentials
                </button>
                <button
                  onClick={() => setActiveTab('advanced')}
                  className={`flex-1 py-4 px-1 text-center border-b-2 font-medium text-sm ${activeTab === 'advanced'
                    ? 'border-blue-600 text-cyan-300'
                    : 'border-transparent text-muted-foreground hover:text-muted-foreground hover:border-border'}`}
                >
                  Advanced
                </button>
              </div>
            </div>

            <div className="p-6">
              {activeTab === 'settings' && (
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-4">General Configuration</h3>
                  <p className="text-muted-foreground mb-6">Configure basic settings for this integration.</p>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {renderFormField('timeout', 'Timeout (seconds)', 'number')}
                    {renderFormField('retry_attempts', 'Retry Attempts', 'number')}
                    {renderFormField('enable_logging', 'Enable Logging', 'checkbox')}
                    {renderFormField('cache_responses', 'Cache Responses', 'checkbox')}
                    {renderFormField('rate_limit', 'Rate Limit (req/min)', 'number')}
                    {renderFormField('concurrency_limit', 'Concurrency Limit', 'number')}
                  </div>
                </div>
              )}

              {activeTab === 'credentials' && (
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-4">API Credentials</h3>
                  <p className="text-muted-foreground mb-6">Enter your API credentials for this integration.</p>

                  <div className="max-w-md">
                    {renderCredentialField('api_key', 'API Key')}
                    {renderCredentialField('secret_key', 'Secret Key')}
                    {renderCredentialField('access_token', 'Access Token')}
                    {renderCredentialField('webhook_url', 'Webhook URL', 'text')}
                  </div>

                  <div className="mt-6 bg-cyan-500/10 border border-blue-200 rounded-lg p-4">
                    <p className="text-blue-800 text-sm">
                      🔒 Your credentials are encrypted and stored securely. They will never be shared or exposed.
                    </p>
                  </div>
                </div>
              )}

              {activeTab === 'advanced' && (
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-4">Advanced Settings</h3>
                  <p className="text-muted-foreground mb-6">Configure advanced options for this integration.</p>

                  <div className="space-y-6">
                    <div>
                      <h4 className="font-medium text-muted-foreground mb-3">Error Handling</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {renderFormField('auto_retry', 'Auto Retry on Failure', 'checkbox')}
                        {renderFormField('retry_delay', 'Retry Delay (ms)', 'number')}
                        {renderFormField('max_retry_delay', 'Max Retry Delay (ms)', 'number')}
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-muted-foreground mb-3">Performance</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {renderFormField('connection_timeout', 'Connection Timeout (ms)', 'number')}
                        {renderFormField('read_timeout', 'Read Timeout (ms)', 'number')}
                        {renderFormField('write_timeout', 'Write Timeout (ms)', 'number')}
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-muted-foreground mb-3">Logging</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {renderFormField('log_level', 'Log Level', 'select', ['DEBUG', 'INFO', 'WARNING', 'ERROR'])}
                        {renderFormField('log_retention_days', 'Log Retention (days)', 'number')}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="border-t border-border px-6 py-4">
              <div className="flex justify-between items-center">
                <div className="flex gap-2">
                  <button
                    onClick={handleTestConnection}
                    disabled={isTesting}
                    className={`bg-cyan-400 text-white px-4 py-2 rounded-md hover:bg-cyan-300 transition-colors ${isTesting ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    {isTesting ? (
                      <>
                        <span className="animate-spin inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full mr-2"></span>
                        Testing...
                      </>
                    ) : (
                      'Test Connection'
                    )}
                  </button>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => navigate(`/app/integrations/${integration.id}`)}
                    className="bg-gray-100 text-muted-foreground px-4 py-2 rounded-md hover:bg-gray-200"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleSave}
                    disabled={isSaving}
                    className={`bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors ${isSaving ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    {isSaving ? (
                      <>
                        <span className="animate-spin inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full mr-2"></span>
                        Saving...
                      </>
                    ) : (
                      'Save Configuration'
                    )}
                  </button>
                </div>
              </div>

              {/* Test Result */}
              {testResult && (
                <div className={`mt-4 p-3 rounded-md ${testResult.success ? 'bg-emerald-500/10 border border-green-200' : 'bg-rose-500/10 border border-red-200'}`}>
                  <p className={testResult.success ? 'text-emerald-300' : 'text-rose-400'}>
                    {testResult.success ? '✅ ' : '❌ '}{testResult.message}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
};

export default IntegrationConfigurationPage;
