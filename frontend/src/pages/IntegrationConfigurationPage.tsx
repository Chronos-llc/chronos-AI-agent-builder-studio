import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ProtectedRoute } from '../components/ProtectedRoute';
import { useAuth } from '../contexts/AuthContext';

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
    const { name, value, type, checked } = e.target;
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
        <label htmlFor={name} className="block text-sm font-medium text-gray-700 mb-1">
          {label}
        </label>
        {type === 'select' ? (
          <select
            id={name}
            name={name}
            value={formData[name] || ''}
            onChange={handleConfigChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
              className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
          </div>
        ) : (
          <input
            type={type}
            id={name}
            name={name}
            value={formData[name] || ''}
            onChange={handleConfigChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        )}
      </div>
    );
  };

  const renderCredentialField = (name: string, label: string, type: string = 'password') => {
    return (
      <div key={name} className="mb-4">
        <label htmlFor={name} className="block text-sm font-medium text-gray-700 mb-1">
          {label}
        </label>
        <input
          type={type}
          id={name}
          name={name}
          value={credentialData[name] || ''}
          onChange={handleCredentialChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder={`Enter ${label.toLowerCase()}`}
        />
      </div>
    );
  };

  if (loading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-gray-50 p-6">
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-lg shadow-sm p-6 animate-pulse">
              <div className="h-8 bg-gray-200 rounded mb-4 w-1/3"></div>
              <div className="h-4 bg-gray-200 rounded mb-2 w-full"></div>
              <div className="h-4 bg-gray-200 rounded mb-4 w-2/3"></div>
              <div className="h-6 bg-gray-200 rounded mb-6 w-1/4"></div>
              <div className="grid grid-cols-2 gap-4">
                <div className="h-4 bg-gray-200 rounded"></div>
                <div className="h-4 bg-gray-200 rounded"></div>
              </div>
            </div>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  if (error) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-gray-50 p-6">
          <div className="max-w-4xl mx-auto">
            <div className="bg-red-50 border border-red-200 rounded-lg p-6">
              <p className="text-red-600 mb-4">⚠️ {error}</p>
              <button
                onClick={() => {
                  if (id) {
                    fetchIntegrationDetails(parseInt(id));
                    fetchIntegrationConfig(parseInt(id));
                  }
                }}
                className="text-sm text-red-600 hover:text-red-800"
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
        <div className="min-h-screen bg-gray-50 p-6">
          <div className="max-w-4xl mx-auto">
            <div className="text-center py-12">
              <div className="text-6xl text-gray-300 mb-4">🔍</div>
              <p className="text-gray-600 mb-2">Integration not found</p>
              <button
                onClick={() => navigate('/integrations')}
                className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
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
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="flex justify-between items-center mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Configure {integration.name}</h1>
              <p className="text-gray-600 mt-1">Customize integration settings and credentials</p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => navigate(`/integrations/${integration.id}`)}
                className="bg-gray-100 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-200"
              >
                ← Back to Details
              </button>
              <button
                onClick={() => navigate('/integrations')}
                className="bg-gray-100 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-200"
              >
                View All Integrations
              </button>
            </div>
          </div>

          {/* Integration Info */}
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <span className="text-blue-600 text-2xl">{integration.icon || '🔌'}</span>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900">{integration.name}</h3>
                <p className="text-gray-600">{integration.description}</p>
                <div className="flex gap-2 mt-2">
                  <span className="text-xs bg-green-100 text-green-600 px-2 py-1 rounded-full">
                    {integration.category.replace('_', ' ')}
                  </span>
                  <span className="text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded-full">
                    {integration.integration_type.replace('_', ' ')}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Configuration Tabs */}
          <div className="bg-white rounded-lg shadow-sm overflow-hidden">
            <div className="border-b border-gray-200 px-6">
              <div className="flex -mb-px">
                <button
                  onClick={() => setActiveTab('settings')}
                  className={`flex-1 py-4 px-1 text-center border-b-2 font-medium text-sm ${activeTab === 'settings' 
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}
                >
                  General Settings
                </button>
                <button
                  onClick={() => setActiveTab('credentials')}
                  className={`flex-1 py-4 px-1 text-center border-b-2 font-medium text-sm ${activeTab === 'credentials'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}
                >
                  Credentials
                </button>
                <button
                  onClick={() => setActiveTab('advanced')}
                  className={`flex-1 py-4 px-1 text-center border-b-2 font-medium text-sm ${activeTab === 'advanced'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}
                >
                  Advanced
                </button>
              </div>
            </div>

            <div className="p-6">
              {activeTab === 'settings' && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">General Configuration</h3>
                  <p className="text-gray-600 mb-6">Configure basic settings for this integration.</p>

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
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">API Credentials</h3>
                  <p className="text-gray-600 mb-6">Enter your API credentials for this integration.</p>

                  <div className="max-w-md">
                    {renderCredentialField('api_key', 'API Key')}
                    {renderCredentialField('secret_key', 'Secret Key')}
                    {renderCredentialField('access_token', 'Access Token')}
                    {renderCredentialField('webhook_url', 'Webhook URL', 'text')}
                  </div>

                  <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <p className="text-blue-800 text-sm">
                      🔒 Your credentials are encrypted and stored securely. They will never be shared or exposed.
                    </p>
                  </div>
                </div>
              )}

              {activeTab === 'advanced' && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Advanced Settings</h3>
                  <p className="text-gray-600 mb-6">Configure advanced options for this integration.</p>

                  <div className="space-y-6">
                    <div>
                      <h4 className="font-medium text-gray-700 mb-3">Error Handling</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {renderFormField('auto_retry', 'Auto Retry on Failure', 'checkbox')}
                        {renderFormField('retry_delay', 'Retry Delay (ms)', 'number')}
                        {renderFormField('max_retry_delay', 'Max Retry Delay (ms)', 'number')}
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-gray-700 mb-3">Performance</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {renderFormField('connection_timeout', 'Connection Timeout (ms)', 'number')}
                        {renderFormField('read_timeout', 'Read Timeout (ms)', 'number')}
                        {renderFormField('write_timeout', 'Write Timeout (ms)', 'number')}
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-gray-700 mb-3">Logging</h4>
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
            <div className="border-t border-gray-200 px-6 py-4">
              <div className="flex justify-between items-center">
                <div className="flex gap-2">
                  <button
                    onClick={handleTestConnection}
                    disabled={isTesting}
                    className={`bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors ${isTesting ? 'opacity-50 cursor-not-allowed' : ''}`}
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
                    onClick={() => navigate(`/integrations/${integration.id}`)}
                    className="bg-gray-100 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-200"
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
                <div className={`mt-4 p-3 rounded-md ${testResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
                  <p className={testResult.success ? 'text-green-600' : 'text-red-600'}>
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