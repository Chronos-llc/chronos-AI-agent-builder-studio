/**
 * ConfigManager Component
 * Advanced Configuration Management System for Chronos AI Agent Builder Studio
 */

import React, { useState, useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { ScrollArea } from '../ui/scroll-area';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import {
  ConfigSchema,
  ConfigVersion,
  ConfigSnapshot,
  EnvironmentType,
  ValidationError,
  DiffEntry,
} from '../../types/configManagement';
import {
  listSchemas,
  listVersions,
  createVersion,
  rollback,
  createSnapshot,
  listSnapshots,
  getEnvironmentConfig,
  updateEnvironmentConfig,
  validateConfig,
  compareConfigs,
} from '../../services/configManagementService';

interface ConfigManagerProps {
  configId: string;
  initialConfig?: Record<string, unknown>;
  onConfigChange?: (config: Record<string, unknown>) => void;
}

const ConfigManager: React.FC<ConfigManagerProps> = ({
  configId,
  initialConfig = {},
  onConfigChange,
}) => {
  // State for configuration data
  const [currentConfig, setCurrentConfig] = useState<Record<string, unknown>>(initialConfig);
  const [selectedSchema, setSelectedSchema] = useState<ConfigSchema | null>(null);
  const [schemas, setSchemas] = useState<ConfigSchema[]>([]);
  const [versions, setVersions] = useState<ConfigVersion[]>([]);
  const [snapshots, setSnapshots] = useState<ConfigSnapshot[]>([]);
  const [selectedEnvironment, setSelectedEnvironment] = useState<EnvironmentType>('DEVELOPMENT');
  const [environmentConfig, setEnvironmentConfig] = useState<Record<string, unknown>>({});
  
  // UI state
  const [isLoading, setIsLoading] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [validationErrors, setValidationErrors] = useState<ValidationError[]>([]);
  const [changelog, setChangelog] = useState('');
  const [jsonEditorValue, setJsonEditorValue] = useState('');
  const [selectedVersion, setSelectedVersion] = useState<ConfigVersion | null>(null);
  const [compareMode, setCompareMode] = useState(false);
  const [compareConfig, setCompareConfig] = useState<Record<string, unknown>>({});
  const [differences, setDifferences] = useState<DiffEntry[]>([]);
  
  // Load schemas on mount
  useEffect(() => {
    loadSchemas();
    loadVersions();
    loadSnapshots();
    loadEnvironmentConfig();
  }, [configId]);
  
  // Update JSON editor when config changes
  useEffect(() => {
    setJsonEditorValue(JSON.stringify(currentConfig, null, 2));
  }, [currentConfig]);
  
  const loadSchemas = async () => {
    try {
      const response = await listSchemas(0, 100);
      setSchemas(response.items);
      if (response.items.length > 0) {
        setSelectedSchema(response.items[0]);
      }
    } catch (error) {
      console.error('Failed to load schemas:', error);
    }
  };
  
  const loadVersions = async () => {
    try {
      const response = await listVersions(configId, 0, 50);
      setVersions(response.items);
    } catch (error) {
      console.error('Failed to load versions:', error);
    }
  };
  
  const loadSnapshots = async () => {
    try {
      const response = await listSnapshots(configId, 0, 50);
      setSnapshots(response.items);
    } catch (error) {
      console.error('Failed to load snapshots:', error);
    }
  };
  
  const loadEnvironmentConfig = async () => {
    try {
      const config = await getEnvironmentConfig(configId, selectedEnvironment);
      setEnvironmentConfig(config.config_data || {});
      setCurrentConfig(config.config_data || initialConfig);
    } catch (error) {
      // Environment config might not exist yet
      setCurrentConfig(initialConfig);
    }
  };
  
  const handleEnvironmentChange = async (env: EnvironmentType) => {
    setSelectedEnvironment(env);
    try {
      const config = await getEnvironmentConfig(configId, env);
      setEnvironmentConfig(config.config_data || {});
      setCurrentConfig(config.config_data || {});
    } catch (error) {
      setCurrentConfig({});
    }
  };
  
  const handleJsonEditorChange = (value: string) => {
    setJsonEditorValue(value);
    try {
      const parsed = JSON.parse(value);
      setCurrentConfig(parsed);
      onConfigChange?.(parsed);
    } catch (e) {
      // Invalid JSON, don't update
    }
  };
  
  const handleValidate = async () => {
    if (!selectedSchema) return;
    
    setIsValidating(true);
    setValidationErrors([]);
    
    try {
      const response = await validateConfig(currentConfig, selectedSchema.id);
      setValidationErrors(response.errors);
    } catch (error) {
      console.error('Validation failed:', error);
      setValidationErrors([{
        path: 'general',
        message: 'Validation request failed',
        error_type: 'request_failed',
      }]);
    } finally {
      setIsValidating(false);
    }
  };
  
  const handleSave = async () => {
    setIsSaving(true);
    
    try {
      await createVersion(configId, {
        config_schema_id: selectedSchema?.id || '',
        configuration_data: currentConfig,
        changelog: changelog || 'Manual save',
      });
      
      setChangelog('');
      loadVersions();
      alert('Configuration saved successfully!');
    } catch (error) {
      console.error('Failed to save:', error);
      alert('Failed to save configuration');
    } finally {
      setIsSaving(false);
    }
  };
  
  const handleSaveEnvironment = async () => {
    setIsSaving(true);
    
    try {
      await updateEnvironmentConfig(configId, selectedEnvironment, currentConfig);
      setEnvironmentConfig(currentConfig);
      alert(`Configuration saved to ${selectedEnvironment} environment successfully!`);
    } catch (error) {
      console.error('Failed to save environment config:', error);
      alert('Failed to save environment configuration');
    } finally {
      setIsSaving(false);
    }
  };
  
  const handleRollback = async (versionId: string) => {
    if (!confirm('Are you sure you want to rollback to this version?')) return;
    
    try {
      const response = await rollback(configId, versionId, 'Rolled back to previous version');
      if (response.success && response.new_version) {
        setCurrentConfig(response.new_version.configuration_data);
        loadVersions();
        alert('Rollback successful!');
      } else {
        alert('Rollback failed: ' + response.message);
      }
    } catch (error) {
      console.error('Rollback failed:', error);
      alert('Rollback failed');
    }
  };
  
  const handleCreateSnapshot = async (type: 'MANUAL' | 'AUTOMATED' | 'SCHEDULED') => {
    try {
      const latestVersion = versions[0];
      if (!latestVersion) {
        alert('No version to snapshot');
        return;
      }
      
      await createSnapshot({
        config_id: configId,
        version_id: latestVersion.id,
        snapshot_data: currentConfig,
        snapshot_type: type,
      });
      
      loadSnapshots();
      alert('Snapshot created successfully!');
    } catch (error) {
      console.error('Failed to create snapshot:', error);
      alert('Failed to create snapshot');
    }
  };
  
  const handleRestoreSnapshot = async (snapshot: ConfigSnapshot) => {
    if (!confirm('Are you sure you want to restore this snapshot?')) return;
    
    setCurrentConfig(snapshot.snapshot_data);
    onConfigChange?.(snapshot.snapshot_data);
    alert('Snapshot restored!');
  };
  
  const handleCompare = async () => {
    try {
      const response = await compareConfigs(currentConfig, compareConfig);
      setDifferences(response.differences);
      setCompareMode(false);
    } catch (error) {
      console.error('Compare failed:', error);
    }
  };
  
  const loadVersionToCompare = (version: ConfigVersion) => {
    setCompareConfig(version.configuration_data);
  };
  
  return (
    <div className="config-manager p-4 space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Configuration Manager</h2>
        <div className="flex gap-2">
          <Select
            value={selectedEnvironment}
            onValueChange={(val) => handleEnvironmentChange(val as EnvironmentType)}
          >
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Environment" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="DEVELOPMENT">Development</SelectItem>
              <SelectItem value="STAGING">Staging</SelectItem>
              <SelectItem value="PRODUCTION">Production</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      
      <Tabs defaultValue="editor" className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="editor">Editor</TabsTrigger>
          <TabsTrigger value="versions">Versions</TabsTrigger>
          <TabsTrigger value="snapshots">Snapshots</TabsTrigger>
          <TabsTrigger value="compare">Diff</TabsTrigger>
          <TabsTrigger value="schemas">Schemas</TabsTrigger>
        </TabsList>
        
        {/* Editor Tab */}
        <TabsContent value="editor" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>JSON Configuration Editor</CardTitle>
              <CardDescription>
                Edit your configuration as JSON. Select a schema to enable validation.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="mb-4">
                <label className="text-sm font-medium">Schema</label>
                <Select
                  value={selectedSchema?.id || ''}
                  onValueChange={(val) => {
                    const schema = schemas.find(s => s.id === val);
                    setSelectedSchema(schema || null);
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a schema" />
                  </SelectTrigger>
                  <SelectContent>
                    {schemas.map((schema) => (
                      <SelectItem key={schema.id} value={schema.id}>
                        {schema.name} ({schema.schema_type})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Configuration (JSON)</label>
                  <textarea
                    className="w-full h-96 p-3 border rounded-md font-mono text-sm bg-gray-50"
                    value={jsonEditorValue}
                    onChange={(e) => handleJsonEditorChange(e.target.value)}
                    placeholder="{}"
                  />
                </div>
                
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <label className="text-sm font-medium">Validation Results</label>
                    <Button
                      size="sm"
                      onClick={handleValidate}
                      disabled={!selectedSchema || isValidating}
                    >
                      {isValidating ? 'Validating...' : 'Validate'}
                    </Button>
                  </div>
                  
                  {validationErrors.length === 0 ? (
                    <div className="h-96 p-4 border rounded-md bg-green-50 text-green-700">
                      ✓ Configuration is valid
                    </div>
                  ) : (
                    <ScrollArea className="h-96 border rounded-md p-4 bg-red-50">
                      {validationErrors.map((error, idx) => (
                        <div key={idx} className="mb-2 p-2 bg-red-100 rounded text-sm">
                          <strong className="text-red-700">{error.path}:</strong>{' '}
                          <span className="text-red-600">{error.message}</span>
                        </div>
                      ))}
                    </ScrollArea>
                  )}
                </div>
              </div>
              
              <div className="mt-4 flex gap-2">
                <Input
                  placeholder="Changelog message (optional)"
                  value={changelog}
                  onChange={(e) => setChangelog(e.target.value)}
                  className="flex-1"
                />
                <Button 
                  onClick={handleSaveEnvironment} 
                  disabled={isSaving}
                  variant="outline"
                >
                  {isSaving ? 'Saving...' : `Save to ${selectedEnvironment}`}
                </Button>
                <Button onClick={handleSave} disabled={isSaving}>
                  {isSaving ? 'Saving...' : 'Save Version'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        {/* Versions Tab */}
        <TabsContent value="versions">
          <Card>
            <CardHeader>
              <CardTitle>Version History</CardTitle>
              <CardDescription>
                View and rollback to previous versions of your configuration.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-96">
                {versions.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">No versions yet</p>
                ) : (
                  <div className="space-y-2">
                    {versions.map((version) => (
                      <div
                        key={version.id}
                        className={`p-4 border rounded-lg ${
                          selectedVersion?.id === version.id ? 'border-blue-500 bg-blue-50' : ''
                        }`}
                      >
                        <div className="flex justify-between items-center">
                          <div>
                            <div className="flex items-center gap-2">
                              <Badge variant="outline">v{version.version_number}</Badge>
                              <span className="text-sm text-gray-500">
                                {new Date(version.created_at).toLocaleString()}
                              </span>
                            </div>
                            {version.changelog && (
                              <p className="text-sm mt-1">{version.changelog}</p>
                            )}
                            {version.created_by && (
                              <p className="text-xs text-gray-400">
                                By: {version.created_by}
                              </p>
                            )}
                          </div>
                          <div className="flex gap-2">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => {
                                setSelectedVersion(version);
                                loadVersionToCompare(version);
                                setCompareMode(true);
                              }}
                            >
                              Compare
                            </Button>
                            <Button
                              size="sm"
                              variant="destructive"
                              onClick={() => handleRollback(version.id)}
                            >
                              Rollback
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>
        
        {/* Snapshots Tab */}
        <TabsContent value="snapshots">
          <Card>
            <CardHeader>
              <CardTitle>Configuration Snapshots</CardTitle>
              <CardDescription>
                Create and restore point-in-time snapshots of your configuration.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="mb-4 flex gap-2">
                <Button onClick={() => handleCreateSnapshot('MANUAL')}>
                  Create Manual Snapshot
                </Button>
              </div>
              
              <ScrollArea className="h-96">
                {snapshots.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">No snapshots yet</p>
                ) : (
                  <div className="space-y-2">
                    {snapshots.map((snapshot) => (
                      <div key={snapshot.id} className="p-4 border rounded-lg">
                        <div className="flex justify-between items-center">
                          <div>
                            <Badge
                              variant={
                                snapshot.snapshot_type === 'MANUAL' ? 'default' :
                                snapshot.snapshot_type === 'AUTOMATED' ? 'secondary' :
                                'outline'
                              }
                            >
                              {snapshot.snapshot_type}
                            </Badge>
                            <span className="text-sm text-gray-500 ml-2">
                              {new Date(snapshot.created_at).toLocaleString()}
                            </span>
                          </div>
                          <Button
                            size="sm"
                            onClick={() => handleRestoreSnapshot(snapshot)}
                          >
                            Restore
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}              
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>
        
        {/* Compare Tab */}
        <TabsContent value="compare">
          <Card>
            <CardHeader>
              <CardTitle>Configuration Diff</CardTitle>
              <CardDescription>
                Compare the current configuration with a previous version.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="mb-4">
                <label className="text-sm font-medium">Compare With Version:</label>
                <Select
                  onValueChange={(val) => {
                    const version = versions.find(v => v.id === val);
                    if (version) loadVersionToCompare(version);
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a version to compare" />
                  </SelectTrigger>
                  <SelectContent>
                    {versions.map((version) => (
                      <SelectItem key={version.id} value={version.id}>
                        v{version.version_number} - {new Date(version.created_at).toLocaleDateString()}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Current Configuration</label>
                  <pre className="h-64 p-3 border rounded-md bg-gray-50 text-sm overflow-auto">
                    {JSON.stringify(currentConfig, null, 2)}
                  </pre>
                </div>
                <div>
                  <label className="text-sm font-medium">Compared Configuration</label>
                  <pre className="h-64 p-3 border rounded-md bg-gray-50 text-sm overflow-auto">
                    {JSON.stringify(compareConfig, null, 2)}
                  </pre>
                </div>
              </div>
              
              <Button className="mt-4" onClick={handleCompare}>
                Compare Configurations
              </Button>
              
              {differences.length > 0 && (
                <div className="mt-4">
                  <h4 className="font-medium mb-2">Differences Found:</h4>
                  <ScrollArea className="h-64 border rounded-md p-4">
                    {differences.map((diff, idx) => (
                      <div
                        key={idx}
                        className={`p-2 mb-2 rounded ${
                          diff.change_type === 'ADDED' ? 'bg-green-100' :
                          diff.change_type === 'REMOVED' ? 'bg-red-100' :
                          'bg-yellow-100'
                        }`}
                      >
                        <Badge
                          variant={
                            diff.change_type === 'ADDED' ? 'default' :
                            diff.change_type === 'REMOVED' ? 'destructive' :
                            'secondary'
                          }
                        >
                          {diff.change_type}
                        </Badge>
                        <span className="ml-2 font-mono text-sm">{diff.path}</span>
                        <div className="mt-1 text-sm">
                          {diff.old_value !== undefined && (
                            <span className="text-red-600">
                              Old: {JSON.stringify(diff.old_value)}
                            </span>
                          )}
                          {diff.new_value !== undefined && (
                            <span className="ml-4 text-green-600">
                              New: {JSON.stringify(diff.new_value)}
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </ScrollArea>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
        
        {/* Schemas Tab */}
        <TabsContent value="schemas">
          <Card>
            <CardHeader>
              <CardTitle>Configuration Schemas</CardTitle>
              <CardDescription>
                View available schemas for configuration validation.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-96">
                {schemas.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">No schemas available</p>
                ) : (
                  <div className="space-y-4">
                    {schemas.map((schema) => (
                      <div key={schema.id} className="p-4 border rounded-lg">
                        <div className="flex justify-between items-center mb-2">
                          <div>
                            <h4 className="font-medium">{schema.name}</h4>
                            <Badge variant="outline">{schema.schema_type}</Badge>
                          </div>
                          <div className="text-sm text-gray-500">
                            Version {schema.version}
                          </div>
                        </div>
                        {schema.description && (
                          <p className="text-sm text-gray-600">{schema.description}</p>
                        )}
                        <details className="mt-2">
                          <summary className="cursor-pointer text-sm text-blue-600">
                            View Schema Definition
                          </summary>
                          <pre className="mt-2 p-3 bg-gray-100 rounded text-xs overflow-auto">
                            {JSON.stringify(schema.schema_definition, null, 2)}
                          </pre>
                        </details>
                      </div>
                    ))}
                  </div>
                )}
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ConfigManager;
