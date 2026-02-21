import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ProtectedRoute } from '../components/ProtectedRoute';
import { useAuth } from '../contexts/AuthContext';
import { ProviderLogo } from '../components/brand/ProviderLogo';
import { PlatformLoadingScreen } from '../components/loading/PlatformLoadingScreen';

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

interface FormField {
  name: string;
  label: string;
  type: string;
  required: boolean;
  placeholder?: string;
  description?: string;
  default?: any;
}

const IntegrationInstallPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [integration, setIntegration] = useState<Integration | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState(1);
  const [configForm, setConfigForm] = useState<Record<string, any>>({});
  const [credentialsForm, setCredentialsForm] = useState<Record<string, any>>({});
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);

  useEffect(() => {
    if (id) {
      fetchIntegrationDetails(parseInt(id));
    }
  }, [id]);

  const buildDefaultFormData = (schema: any): Record<string, any> => {
    if (!schema || typeof schema !== 'object') {
      return {};
    }

    const properties = schema.properties || schema;
    const defaults: Record<string, any> = {};

    Object.entries(properties).forEach(([name, field]) => {
      const fieldConfig: any = (typeof field === 'object' && field !== null) ? field : {};
      if (fieldConfig.default !== undefined) {
        defaults[name] = fieldConfig.default;
      }
    });

    return defaults;
  };

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
      setConfigForm(buildDefaultFormData(data.config_schema));
      setCredentialsForm(buildDefaultFormData(data.credentials_schema));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch integration details');
    } finally {
      setLoading(false);
    }
  };

  const handleConfigChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target as HTMLInputElement;
    const parsedValue = type === 'checkbox'
      ? (e.target as HTMLInputElement).checked
      : type === 'number'
        ? parseFloat(value)
        : value;
    setConfigForm({
      ...configForm,
      [name]: parsedValue
    });
  };

  const handleCredentialsChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setCredentialsForm({
      ...credentialsForm,
      [name]: value
    });
  };

  const handleTestConnection = async () => {
    if (!integration) return;

    setIsTesting(true);
    setTestResult(null);

    try {
      // Simulate API test
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

  const handleInstall = async () => {
    if (!integration || !user) return;

    try {
      const response = await fetch(`/api/v1/integrations/${integration.id}/config/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          config: configForm,
          credentials: credentialsForm,
          is_active: true
        })
      });

      if (!response.ok) {
        throw new Error('Failed to install integration');
      }

      const data = await response.json();
      navigate(`/app/integrations/${integration.id}/success?config_id=${data.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to install integration');
    }
  };

  const getFormFields = (schema: any): FormField[] => {
    if (!schema || typeof schema !== 'object') {
      return [];
    }

    const properties = schema.properties || schema;
    const requiredFields = new Set(schema.required || []);

    return Object.entries(properties).map(([name, field]) => {
      const fieldConfig: any = (typeof field === 'object' && field !== null) ? field : {};
      const isSensitive = fieldConfig.sensitive || fieldConfig.format === 'password';
      const fieldType = isSensitive ? 'password' : (fieldConfig.type || 'text');

      return {
        name,
        label: fieldConfig.title || name,
        type: fieldType,
        required: requiredFields.has(name) || fieldConfig.required || false,
        placeholder: fieldConfig.description || `Enter ${name}`,
        description: fieldConfig.description,
        default: fieldConfig.default
      };
    });
  };

  const renderFormField = (
    field: FormField,
    formData: Record<string, any>,
    onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void
  ) => {
    return (
      <div key={field.name} className="mb-4">
        <label htmlFor={field.name} className="block text-sm font-medium text-muted-foreground mb-1">
          {field.label}
        </label>
        {field.description && (
          <p className="text-xs text-muted-foreground mb-1">{field.description}</p>
        )}
        {field.type === 'boolean' ? (
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              id={field.name}
              name={field.name}
              checked={formData[field.name] ?? field.default ?? false}
              onChange={onChange}
              className="rounded border-border text-cyan-300 focus:ring-blue-500"
            />
            <span className="text-sm text-muted-foreground">Enabled</span>
          </label>
        ) : field.type === 'textarea' ? (
          <textarea
            id={field.name}
            name={field.name}
            value={formData[field.name] ?? field.default ?? ''}
            onChange={onChange}
            rows={3}
            className="w-full px-3 py-2 border border-border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder={field.placeholder}
            required={field.required}
          />
        ) : (
          <input
            type={field.type === 'password' ? 'password' : field.type === 'number' ? 'number' : 'text'}
            id={field.name}
            name={field.name}
            value={formData[field.name] ?? field.default ?? ''}
            onChange={onChange}
            className="w-full px-3 py-2 border border-border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder={field.placeholder}
            required={field.required}
          />
        )}
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
                onClick={() => fetchIntegrationDetails(parseInt(id || '0'))}
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

  const configFields = getFormFields(integration.config_schema);
  const credentialFields = getFormFields(integration.credentials_schema);

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-background p-6">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="flex justify-between items-center mb-6">
            <div className="flex items-center gap-3">
              <ProviderLogo
                name={integration.name}
                url={integration.icon}
                size={38}
                className="border-0 bg-transparent"
              />
              <div>
              <h1 className="text-3xl font-bold text-foreground">Install {integration.name}</h1>
              <p className="text-muted-foreground mt-1">Follow the steps to integrate with your agents</p>
              </div>
            </div>
            <button
              onClick={() => navigate(`/app/integrations/${integration.id}`)}
              className="bg-gray-100 text-muted-foreground px-4 py-2 rounded-md hover:bg-gray-200"
            >
              ← Back to Details
            </button>
          </div>

          {/* Progress Steps */}
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-4">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${step >= 1 ? 'bg-cyan-400 text-white' : 'bg-gray-200 text-muted-foreground'}`}>
                1
              </div>
              <span className={`text-sm font-medium ${step >= 1 ? 'text-foreground' : 'text-muted-foreground/70'}`}>Configuration</span>
            </div>

            <div className={`flex-1 h-0.5 ${step >= 2 ? 'bg-cyan-400' : 'bg-gray-200'}`}></div>

            <div className="flex items-center gap-4">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${step >= 2 ? 'bg-cyan-400 text-white' : 'bg-gray-200 text-muted-foreground'}`}>
                2
              </div>
              <span className={`text-sm font-medium ${step >= 2 ? 'text-foreground' : 'text-muted-foreground/70'}`}>Credentials</span>
            </div>

            <div className={`flex-1 h-0.5 ${step >= 3 ? 'bg-cyan-400' : 'bg-gray-200'}`}></div>

            <div className="flex items-center gap-4">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${step >= 3 ? 'bg-cyan-400 text-white' : 'bg-gray-200 text-muted-foreground'}`}>
                3
              </div>
              <span className={`text-sm font-medium ${step >= 3 ? 'text-foreground' : 'text-muted-foreground/70'}`}>Test & Install</span>
            </div>
          </div>

          {/* Installation Form */}
          <div className="bg-card rounded-lg shadow-sm overflow-hidden">
            <div className="p-6">
              {step === 1 && (
                <div>
                  <h3 className="text-xl font-semibold text-foreground mb-4">Configuration Settings</h3>
                  <p className="text-muted-foreground mb-6">Configure the basic settings for this integration.</p>

                  {configFields.length > 0 ? (
                    <form className="space-y-4">
                      {configFields.map(field => renderFormField(field, configForm, handleConfigChange))}
                    </form>
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-muted-foreground">No configuration required for this integration</p>
                    </div>
                  )}
                </div>
              )}

              {step === 2 && (
                <div>
                  <h3 className="text-xl font-semibold text-foreground mb-4">Credentials Setup</h3>
                  <p className="text-muted-foreground mb-6">Enter your API credentials for this integration.</p>

                  {credentialFields.length > 0 ? (
                    <form className="space-y-4">
                      {credentialFields.map(field => renderFormField(field, credentialsForm, handleCredentialsChange))}
                    </form>
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-muted-foreground">No credentials required for this integration</p>
                    </div>
                  )}
                </div>
              )}

              {step === 3 && (
                <div>
                  <h3 className="text-xl font-semibold text-foreground mb-4">Test Connection</h3>
                  <p className="text-muted-foreground mb-6">Test your configuration before finalizing the installation.</p>

                  <div className="bg-background rounded-lg p-4 mb-6">
                    <h4 className="font-medium text-muted-foreground mb-2">Configuration Summary</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground mb-1">Integration Type</p>
                        <p className="font-medium">{integration.integration_type.replace('_', ' ')}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground mb-1">Category</p>
                        <p className="font-medium">{integration.category.replace('_', ' ')}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground mb-1">Config Fields</p>
                        <p className="font-medium">{configFields.length} fields configured</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground mb-1">Credential Fields</p>
                        <p className="font-medium">{credentialFields.length} fields configured</p>
                      </div>
                    </div>
                  </div>

                  <div className="mb-6">
                    <h4 className="font-medium text-muted-foreground mb-3">Test Connection</h4>
                    <button
                      onClick={handleTestConnection}
                      disabled={isTesting}
                      className={`w-full bg-cyan-400 text-white py-2 px-4 rounded-md hover:bg-cyan-300 transition-colors ${isTesting ? 'opacity-50 cursor-not-allowed' : ''}`}
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

                    {testResult && (
                      <div className={`mt-4 p-3 rounded-md ${testResult.success ? 'bg-emerald-500/10 border border-green-200' : 'bg-rose-500/10 border border-red-200'}`}>
                        <p className={testResult.success ? 'text-emerald-300' : 'text-rose-400'}>
                          {testResult.success ? '✅ ' : '❌ '}{testResult.message}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Navigation Buttons */}
            <div className="border-t border-border px-6 py-4">
              <div className="flex justify-between items-center">
                <button
                  onClick={() => step > 1 ? setStep(step - 1) : navigate(`/app/integrations/${integration.id}`)}
                  className="bg-gray-100 text-muted-foreground px-4 py-2 rounded-md hover:bg-gray-200"
                >
                  {step > 1 ? '← Previous' : 'Cancel'}
                </button>

                {step < 3 ? (
                  <button
                    onClick={() => setStep(step + 1)}
                    className="bg-cyan-400 text-white px-4 py-2 rounded-md hover:bg-cyan-300"
                  >
                    Next →
                  </button>
                ) : (
                  <button
                    onClick={handleInstall}
                    disabled={isTesting || (!!testResult && !testResult.success)}
                    className={`bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 ${isTesting || (!!testResult && !testResult.success) ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    Install Integration
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
};

export default IntegrationInstallPage;
