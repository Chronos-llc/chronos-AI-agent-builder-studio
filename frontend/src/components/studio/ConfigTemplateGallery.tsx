/**
 * ConfigTemplateGallery Component
 * Template browser with categories, preview, and one-click application
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { ScrollArea } from '../ui/scroll-area';
import { Input } from '../ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import {
  ConfigTemplate,
  ConfigTemplateCreate,
  SchemaType,
} from '../../types/configManagement';
import {
  listTemplates,
  createTemplate,
  deleteTemplate,
  applyTemplate,
  listSchemas,
} from '../../services/configManagementService';

interface ConfigTemplateGalleryProps {
  onTemplateApply?: (templateId: string, parameters: Record<string, unknown>, result: Record<string, unknown>) => void;
  onTemplateSelect?: (template: ConfigTemplate) => void;
}

const ConfigTemplateGallery: React.FC<ConfigTemplateGalleryProps> = ({
  onTemplateApply,
  onTemplateSelect,
}) => {
  const [templates, setTemplates] = useState<ConfigTemplate[]>([]);
  const [schemas, setSchemas] = useState<ConfigSchema[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<ConfigTemplate | null>(null);
  const [previewConfig, setPreviewConfig] = useState<Record<string, unknown>>({});
  const [parameters, setParameters] = useState<Record<string, unknown>>({});
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState<SchemaType | 'ALL'>('ALL');
  const [isCreating, setIsCreating] = useState(false);
  const [isApplying, setIsApplying] = useState(false);
  
  // Form state for creating templates
  const [formName, setFormName] = useState('');
  const [formDescription, setFormDescription] = useState('');
  const [formSchemaId, setFormSchemaId] = useState('');
  const [formTemplateData, setFormTemplateData] = useState('{\n  "type": "object",\n  "properties": {}\n}');
  const [formParameters, setFormParameters] = useState('{\n  "param1": {\n    "type": "string",\n    "description": "Parameter description"\n  }\n}');
  const [formIsPublic, setFormIsPublic] = useState(false);
  
  useEffect(() => {
    loadTemplates();
    loadSchemas();
  }, []);
  
  useEffect(() => {
    if (selectedTemplate) {
      updatePreview();
    }
  }, [selectedTemplate, parameters]);
  
  const loadTemplates = async () => {
    setIsLoading(true);
    try {
      const response = await listTemplates(0, 100);
      setTemplates(response.items);
    } catch (error) {
      console.error('Failed to load templates:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const loadSchemas = async () => {
    try {
      const response = await listSchemas(0, 100);
      setSchemas(response.items);
      if (response.items.length > 0) {
        setFormSchemaId(response.items[0].id);
      }
    } catch (error) {
      console.error('Failed to load schemas:', error);
    }
  };
  
  const updatePreview = async () => {
    if (!selectedTemplate) return;
    
    try {
      const response = await applyTemplate(selectedTemplate.id, parameters);
      setPreviewConfig(response.applied_config);
    } catch (error) {
      console.error('Failed to generate preview:', error);
    }
  };
  
  const handleApplyTemplate = async (template: ConfigTemplate) => {
    setIsApplying(true);
    try {
      const response = await applyTemplate(template.id, parameters);
      onTemplateApply?.(template.id, parameters, response.applied_config);
      alert('Template applied successfully!');
    } catch (error) {
      console.error('Failed to apply template:', error);
      alert('Failed to apply template');
    } finally {
      setIsApplying(false);
    }
  };
  
  const handleCreateTemplate = async () => {
    try {
      const templateData = JSON.parse(formTemplateData);
      const paramDefs = JSON.parse(formParameters);
      
      await createTemplate({
        name: formName,
        description: formDescription,
        config_schema_id: formSchemaId,
        template_data: templateData,
        parameters: paramDefs,
        is_public: formIsPublic,
      });
      
      setIsCreating(false);
      resetCreateForm();
      loadTemplates();
      alert('Template created successfully!');
    } catch (error) {
      console.error('Failed to create template:', error);
      alert('Failed to create template');
    }
  };
  
  const handleDeleteTemplate = async (templateId: string) => {
    if (!confirm('Are you sure you want to delete this template?')) return;
    
    try {
      await deleteTemplate(templateId);
      if (selectedTemplate?.id === templateId) {
        setSelectedTemplate(null);
      }
      loadTemplates();
      alert('Template deleted successfully!');
    } catch (error) {
      console.error('Failed to delete template:', error);
      alert('Failed to delete template');
    }
  };
  
  const resetCreateForm = () => {
    setFormName('');
    setFormDescription('');
    setFormTemplateData('{\n  "type": "object",\n  "properties": {}\n}');
    setFormParameters('{\n  "param1": {\n    "type": "string",\n    "description": "Parameter description"\n  }\n}');
    setFormIsPublic(false);
  };
  
  const filteredTemplates = templates.filter((template) => {
    // Search filter
    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      if (
        !template.name.toLowerCase().includes(search) &&
        !template.description?.toLowerCase().includes(search)
      ) {
        return false;
      }
    }
    
    // Type filter
    const schema = schemas.find(s => s.id === template.config_schema_id);
    if (typeFilter !== 'ALL' && schema?.schema_type !== typeFilter) {
      return false;
    }
    
    return true;
  });
  
  const getSchemaType = (template: ConfigTemplate): SchemaType => {
    const schema = schemas.find(s => s.id === template.config_schema_id);
    return schema?.schema_type || 'CUSTOM';
  };
  
  return (
    <div className="config-template-gallery p-4 space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Template Gallery</h2>
        <Button onClick={() => setIsCreating(true)}>
          Create Template
        </Button>
      </div>
      
      {/* Create Template Modal */}
      {isCreating && (
        <Card>
          <CardHeader>
            <CardTitle>Create New Template</CardTitle>
            <CardDescription>
              Create a reusable configuration template
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="text-sm font-medium">Template Name</label>
                <Input
                  value={formName}
                  onChange={(e) => setFormName(e.target.value)}
                  placeholder="My Template"
                />
              </div>
              <div>
                <label className="text-sm font-medium">Schema</label>
                <Select value={formSchemaId} onValueChange={setFormSchemaId}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a schema" />
                  </SelectTrigger>
                  <SelectContent>
                    {schemas.map((schema) => (
                      <SelectItem key={schema.id} value={schema.id}>
                        {schema.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div className="mb-4">
              <label className="text-sm font-medium">Description</label>
              <Input
                value={formDescription}
                onChange={(e) => setFormDescription(e.target.value)}
                placeholder="Template description"
              />
            </div>
            
            <div className="mb-4">
              <label className="text-sm font-medium">Template Data (JSON)</label>
              <textarea
                className="w-full h-32 p-3 border rounded-md font-mono text-sm bg-gray-50"
                value={formTemplateData}
                onChange={(e) => setFormTemplateData(e.target.value)}
              />
            </div>
            
            <div className="mb-4">
              <label className="text-sm font-medium">Parameters Definition (JSON)</label>
              <textarea
                className="w-full h-32 p-3 border rounded-md font-mono text-sm bg-gray-50"
                value={formParameters}
                onChange={(e) => setFormParameters(e.target.value)}
              />
            </div>
            
            <div className="mb-4">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={formIsPublic}
                  onChange={(e) => setFormIsPublic(e.target.checked)}
                />
                <span className="text-sm font-medium">Make template public</span>
              </label>
            </div>
            
            <div className="flex gap-2">
              <Button onClick={handleCreateTemplate}>Create Template</Button>
              <Button variant="outline" onClick={() => setIsCreating(false)}>
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
      
      <div className="grid grid-cols-3 gap-4">
        {/* Template List */}
        <div className="col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>Templates</CardTitle>
              <div className="mt-2 space-y-2">
                <Input
                  placeholder="Search templates..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
                <Select
                  value={typeFilter}
                  onValueChange={(val) => setTypeFilter(val as SchemaType | 'ALL')}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Filter by type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ALL">All Types</SelectItem>
                    <SelectItem value="AGENT">Agent</SelectItem>
                    <SelectItem value="WORKFLOW">Workflow</SelectItem>
                    <SelectItem value="SYSTEM">System</SelectItem>
                    <SelectItem value="CUSTOM">Custom</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-96">
                {isLoading ? (
                  <p className="text-gray-500 text-center py-8">Loading templates...</p>
                ) : filteredTemplates.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">No templates found</p>
                ) : (
                  <div className="space-y-2">
                    {filteredTemplates.map((template) => (
                      <div
                        key={template.id}
                        className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                          selectedTemplate?.id === template.id
                            ? 'border-blue-500 bg-blue-50'
                            : 'hover:bg-gray-50'
                        }`}
                        onClick={() => {
                          setSelectedTemplate(template);
                          onTemplateSelect?.(template);
                        }}
                      >
                        <div className="flex justify-between items-start">
                          <div>
                            <h4 className="font-medium text-sm">{template.name}</h4>
                            <Badge variant="outline" className="mt-1">
                              {getSchemaType(template)}
                            </Badge>
                            {template.is_public && (
                              <Badge className="ml-1" variant="secondary">
                                Public
                              </Badge>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </ScrollArea>
            </CardContent>
          </Card>
        </div>
        
        {/* Template Details & Preview */}
        <div className="col-span-2">
          {selectedTemplate ? (
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle>{selectedTemplate.name}</CardTitle>
                      <CardDescription>{selectedTemplate.description}</CardDescription>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => handleDeleteTemplate(selectedTemplate.id)}
                      >
                        Delete
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <Tabs defaultValue="preview">
                    <TabsList>
                      <TabsTrigger value="preview">Preview</TabsTrigger>
                      <TabsTrigger value="parameters">Parameters</TabsTrigger>
                      <TabsTrigger value="template">Template Data</TabsTrigger>
                    </TabsList>
                    
                    <TabsContent value="preview">
                      <div className="mt-4">
                        <h4 className="font-medium mb-2">Preview Result</h4>
                        <pre className="h-64 p-3 border rounded-md bg-gray-50 text-sm overflow-auto">
                          {JSON.stringify(previewConfig, null, 2)}
                        </pre>
                        <Button
                          className="mt-4"
                          onClick={() => handleApplyTemplate(selectedTemplate)}
                          disabled={isApplying}
                        >
                          {isApplying ? 'Applying...' : 'Apply Template'}
                        </Button>
                      </div>
                    </TabsContent>
                    
                    <TabsContent value="parameters">
                      <div className="mt-4">
                        <h4 className="font-medium mb-2">Template Parameters</h4>
                        {selectedTemplate.parameters ? (
                          <div className="space-y-4">
                            {Object.entries(selectedTemplate.parameters).map(([key, param]) => (
                              <div key={key} className="p-3 border rounded-lg">
                                <div className="flex items-center gap-2 mb-2">
                                  <code className="text-sm font-mono">{key}</code>
                                  {(param as { type?: string }).type && (
                                    <Badge variant="secondary">{(param as { type: string }).type}</Badge>
                                  )}
                                </div>
                                {(param as { description?: string }).description && (
                                  <p className="text-sm text-gray-600">
                                    {(param as { description: string }).description}
                                  </p>
                                )}
                                <Input
                                  placeholder={`Enter ${key}`}
                                  className="mt-2"
                                  value={(parameters[key] as string) || ''}
                                  onChange={(e) => setParameters({
                                    ...parameters,
                                    [key]: e.target.value,
                                  })}
                                />
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="text-gray-500">No parameters defined</p>
                        )}
                      </div>
                    </TabsContent>
                    
                    <TabsContent value="template">
                      <div className="mt-4">
                        <h4 className="font-medium mb-2">Template Data</h4>
                        <pre className="h-64 p-3 border rounded-md bg-gray-50 text-sm overflow-auto">
                          {JSON.stringify(selectedTemplate.template_data, null, 2)}
                        </pre>
                      </div>
                    </TabsContent>
                  </Tabs>
                </CardContent>
              </Card>
            </div>
          ) : (
            <Card>
              <CardContent className="flex items-center justify-center h-96">
                <p className="text-gray-500">
                  Select a template to view details and preview
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default ConfigTemplateGallery;
