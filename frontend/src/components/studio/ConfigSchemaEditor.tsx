/**
 * ConfigSchemaEditor Component
 * JSON Schema editor with validation rules and version management
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { ScrollArea } from '../ui/scroll-area';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import {
  ConfigSchema,
  ConfigSchemaCreate,
  ConfigSchemaUpdate,
  SchemaType,
} from '../../types/configManagement';
import {
  listSchemas,
  createSchema,
  updateSchema,
  deleteSchema,
} from '../../services/configManagementService';

interface ConfigSchemaEditorProps {
  onSchemaSelect?: (schema: ConfigSchema) => void;
}

const ConfigSchemaEditor: React.FC<ConfigSchemaEditorProps> = ({ onSchemaSelect }) => {
  const [schemas, setSchemas] = useState<ConfigSchema[]>([]);
  const [selectedSchema, setSelectedSchema] = useState<ConfigSchema | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  
  // Form state
  const [formName, setFormName] = useState('');
  const [formDescription, setFormDescription] = useState('');
  const [formType, setFormType] = useState<SchemaType>('CUSTOM');
  const [formDefinition, setFormDefinition] = useState<string>('{\n  "type": "object",\n  "properties": {}\n}');
  const [jsonError, setJsonError] = useState<string | null>(null);
  
  useEffect(() => {
    loadSchemas();
  }, []);
  
  const loadSchemas = async () => {
    setIsLoading(true);
    try {
      const response = await listSchemas(0, 100);
      setSchemas(response.items);
    } catch (error) {
      console.error('Failed to load schemas:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleDefinitionChange = (value: string) => {
    setFormDefinition(value);
    try {
      JSON.parse(value);
      setJsonError(null);
    } catch (e) {
      setJsonError('Invalid JSON: ' + (e as Error).message);
    }
  };
  
  const handleCreate = async () => {
    if (jsonError) {
      alert('Please fix JSON errors before saving');
      return;
    }
    
    try {
      const definition = JSON.parse(formDefinition);
      const createData: ConfigSchemaCreate = {
        name: formName,
        description: formDescription,
        schema_type: formType,
        schema_definition: definition,
      };
      await createSchema(createData);
      
      setIsCreating(false);
      resetForm();
      loadSchemas();
      alert('Schema created successfully!');
    } catch (error) {
      console.error('Failed to create schema:', error);
      alert('Failed to create schema');
    }
  };
  
  const handleUpdate = async () => {
    if (!selectedSchema || jsonError) return;
    
    try {
      const definition = JSON.parse(formDefinition);
      const updateData: ConfigSchemaUpdate = {
        name: formName,
        description: formDescription,
        schema_type: formType,
        schema_definition: definition,
      };
      await updateSchema(selectedSchema.id, updateData);
      
      setIsEditing(false);
      loadSchemas();
      alert('Schema updated successfully!');
    } catch (error) {
      console.error('Failed to update schema:', error);
      alert('Failed to update schema');
    }
  };
  
  const handleDelete = async (schemaId: string) => {
    if (!confirm('Are you sure you want to delete this schema?')) return;
    
    try {
      await deleteSchema(schemaId);
      loadSchemas();
      if (selectedSchema?.id === schemaId) {
        setSelectedSchema(null);
      }
      alert('Schema deleted successfully!');
    } catch (error) {
      console.error('Failed to delete schema:', error);
      alert('Failed to delete schema');
    }
  };
  
  const resetForm = () => {
    setFormName('');
    setFormDescription('');
    setFormType('CUSTOM');
    setFormDefinition('{\n  "type": "object",\n  "properties": {}\n}');
    setJsonError(null);
  };
  
  const startEditing = (schema: ConfigSchema) => {
    setSelectedSchema(schema);
    setFormName(schema.name);
    setFormDescription(schema.description || '');
    setFormType(schema.schema_type);
    setFormDefinition(JSON.stringify(schema.schema_definition, null, 2));
    setIsEditing(true);
    setIsCreating(false);
  };
  
  const startCreating = () => {
    resetForm();
    setIsCreating(true);
    setIsEditing(false);
    setSelectedSchema(null);
  };
  
  const handleSchemaSelect = (schema: ConfigSchema) => {
    setSelectedSchema(schema);
    onSchemaSelect?.(schema);
  };
  
  return (
    <div className="config-schema-editor p-4 space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Schema Editor</h2>
        <Button onClick={startCreating}>
          Create New Schema
        </Button>
      </div>
      
      {(isCreating || isEditing) && (
        <Card>
          <CardHeader>
            <CardTitle>
              {isCreating ? 'Create New Schema' : `Edit Schema: ${selectedSchema?.name}`}
            </CardTitle>
            <CardDescription>
              Define a JSON Schema for configuration validation
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="text-sm font-medium">Schema Name</label>
                <Input
                  value={formName}
                  onChange={(e) => setFormName(e.target.value)}
                  placeholder="My Configuration Schema"
                />
              </div>
              <div>
                <label className="text-sm font-medium">Schema Type</label>
                <Select value={formType} onValueChange={(val) => setFormType(val as SchemaType)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="AGENT">Agent</SelectItem>
                    <SelectItem value="WORKFLOW">Workflow</SelectItem>
                    <SelectItem value="SYSTEM">System</SelectItem>
                    <SelectItem value="CUSTOM">Custom</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div className="mb-4">
              <label className="text-sm font-medium">Description</label>
              <Input
                value={formDescription}
                onChange={(e) => setFormDescription(e.target.value)}
                placeholder="Description of this schema"
              />
            </div>
            
            <div className="mb-4">
              <div className="flex justify-between items-center mb-2">
                <label 
                  htmlFor="schema-definition"
                  className="text-sm font-medium"
                >
                  JSON Schema Definition
                </label>
                {jsonError ? (
                  <Badge variant="destructive">{jsonError}</Badge>
                ) : (
                  <Badge variant="default">Valid JSON</Badge>
                )}
              </div>
              <textarea
                id="schema-definition"
                className={`w-full h-64 p-3 border rounded-md font-mono text-sm ${
                  jsonError ? 'border-red-500 bg-red-50' : 'bg-gray-50'
                }`}
                value={formDefinition}
                onChange={(e) => handleDefinitionChange(e.target.value)}
                placeholder='{"type": "object", "properties": {}}'
                aria-label="JSON Schema Definition"
              />
            </div>
            
            <div className="flex gap-2">
              <Button onClick={isCreating ? handleCreate : handleUpdate} disabled={!!jsonError}>
                {isCreating ? 'Create Schema' : 'Update Schema'}
              </Button>
              <Button variant="outline" onClick={() => {
                setIsCreating(false);
                setIsEditing(false);
              }}>
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
      
      <Card>
        <CardHeader>
          <CardTitle>Available Schemas</CardTitle>
          <CardDescription>
            Select a schema to view details or use for configuration validation
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-96">
            {isLoading ? (
              <p className="text-gray-500 text-center py-8">Loading schemas...</p>
            ) : schemas.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No schemas available</p>
            ) : (
              <div className="space-y-4">
                {schemas.map((schema) => (
                  <div
                    key={schema.id}
                    className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                      selectedSchema?.id === schema.id
                        ? 'border-blue-500 bg-blue-50'
                        : 'hover:bg-gray-50'
                    }`}
                    onClick={() => handleSchemaSelect(schema)}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h4 className="font-medium">{schema.name}</h4>
                          <Badge variant="outline">{schema.schema_type}</Badge>
                          <Badge variant="secondary">v{schema.version}</Badge>
                          {!schema.is_active && (
                            <Badge variant="destructive">Inactive</Badge>
                          )}
                        </div>
                        {schema.description && (
                          <p className="text-sm text-gray-600 mt-1">{schema.description}</p>
                        )}
                        <p className="text-xs text-gray-400 mt-2">
                          Created: {new Date(schema.created_at).toLocaleString()}
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={(e) => {
                            e.stopPropagation();
                            startEditing(schema);
                          }}
                        >
                          Edit
                        </Button>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDelete(schema.id);
                          }}
                        >
                          Delete
                        </Button>
                      </div>
                    </div>
                    
                    {selectedSchema?.id === schema.id && (
                      <div className="mt-4 p-3 bg-gray-100 rounded">
                        <details>
                          <summary className="cursor-pointer text-sm font-medium">
                            Schema Definition Preview
                          </summary>
                          <pre className="mt-2 text-xs overflow-auto max-h-64">
                            {JSON.stringify(schema.schema_definition, null, 2)}
                          </pre>
                        </details>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
};

export default ConfigSchemaEditor;
