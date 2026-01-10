import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { 
  Sparkles, Loader2, Copy, Check,
  RefreshCw, Settings, ChevronDown, ChevronUp 
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { ScrollArea } from '../ui/scroll-area';
import { workflowGenerationService } from '../../services/workflowGenerationService';
import type { 
  WorkflowGenerationRequest, 
  WorkflowGenerationResponse,
  WorkflowSchema
} from '../../types/workflowGeneration';

interface AIWorkflowGeneratorProps {
  onWorkflowGenerated?: (workflow: WorkflowGenerationResponse) => void;
  onLoadToBuilder?: (schema: WorkflowSchema) => void;
}

export const AIWorkflowGenerator: React.FC<AIWorkflowGeneratorProps> = ({
  onWorkflowGenerated,
  onLoadToBuilder,
}) => {
  const [description, setDescription] = useState('');
  const [parameters, setParameters] = useState('{}');
  const [category, setCategory] = useState<string>('');
  const [isExpanded, setIsExpanded] = useState(true);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const generateMutation = useMutation({
    mutationFn: async (request: WorkflowGenerationRequest) => {
      return workflowGenerationService.generateWorkflow(
        request.description,
        request.parameters,
        request.category
      );
    },
    onSuccess: (data) => {
      onWorkflowGenerated?.(data);
    },
    onError: (error: Error) => {
      console.error('Workflow generation failed:', error);
    },
  });

  const templatesQuery = useQuery({
    queryKey: ['workflow-templates'],
    queryFn: () => workflowGenerationService.listTemplates(undefined, true, 5),
  });

  const patternsQuery = useQuery({
    queryKey: ['workflow-patterns'],
    queryFn: () => workflowGenerationService.listPatterns(),
  });

  const handleGenerate = () => {
    if (!description.trim()) return;

    let parsedParameters = {};
    try {
      parsedParameters = JSON.parse(parameters);
    } catch {
      // Use empty object if parsing fails
    }

    generateMutation.mutate({
      description: description.trim(),
      parameters: parsedParameters,
      category: (category || undefined) as any,
    });
  };

  const handleCopySchema = async (schema: WorkflowSchema) => {
    await navigator.clipboard.writeText(JSON.stringify(schema, null, 2));
    setCopiedId('schema');
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleLoadToBuilder = (schema: WorkflowSchema) => {
    onLoadToBuilder?.(schema);
  };

  const handleQuickGenerate = (templateDescription: string) => {
    setDescription(templateDescription);
  };

  const categoryOptions = [
    { value: '', label: 'Auto-detect' },
    { value: 'data_processing', label: 'Data Processing' },
    { value: 'api_integration', label: 'API Integration' },
    { value: 'automation', label: 'Automation' },
    { value: 'etl', label: 'ETL' },
    { value: 'machine_learning', label: 'Machine Learning' },
    { value: 'document_processing', label: 'Document Processing' },
    { value: 'notification', label: 'Notification' },
    { value: 'scheduling', label: 'Scheduling' },
  ];

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-primary" />
          <h2 className="font-semibold">AI Workflow Generator</h2>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          {isExpanded ? (
            <ChevronUp className="w-4 h-4" />
          ) : (
            <ChevronDown className="w-4 h-4" />
          )}
        </Button>
      </div>

      <div className="flex-1 overflow-hidden flex flex-col">
        {isExpanded && (
          <ScrollArea className="flex-1">
            <div className="p-4 space-y-6">
              {/* Input Section */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Describe Your Workflow</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">
                      What should the workflow do?
                    </label>
                    <textarea
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      placeholder="e.g., Create a workflow that fetches data from an API, transforms it, and saves it to a database..."
                      className="w-full px-3 py-2 border border-input rounded-md bg-background min-h-[100px]"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label htmlFor="workflow-category" className="block text-sm font-medium mb-1">Category</label>
                      <select
                        id="workflow-category"
                        value={category}
                        onChange={(e) => setCategory(e.target.value)}
                        className="w-full px-3 py-2 border border-input rounded-md bg-background"
                      >
                        {categoryOptions.map((opt) => (
                          <option key={opt.value} value={opt.value}>
                            {opt.label}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">
                        Parameters (JSON)
                      </label>
                      <Input
                        value={parameters}
                        onChange={(e) => setParameters(e.target.value)}
                        placeholder='{"key": "value"}'
                      />
                    </div>
                  </div>

                  <Button
                    onClick={handleGenerate}
                    disabled={!description.trim() || generateMutation.isPending}
                    className="w-full"
                  >
                    {generateMutation.isPending ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4 mr-2" />
                        Generate Workflow
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>

              {/* Quick Start Templates */}
              {templatesQuery.isSuccess && templatesQuery.data.templates.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Quick Start Templates</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 gap-2">
                      {templatesQuery.data.templates.map((template) => (
                        <button
                          key={template.id}
                          onClick={() => handleQuickGenerate(
                            `Create a workflow based on template: ${template.name}. ${template.description || ''}`
                          )}
                          className="text-left p-3 rounded-lg border border-border hover:bg-accent transition-colors"
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-medium">{template.name}</span>
                            <Badge variant="outline">{template.category}</Badge>
                          </div>
                          {template.description && (
                            <p className="text-sm text-muted-foreground mt-1">
                              {template.description}
                            </p>
                          )}
                        </button>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Generated Workflow Preview */}
              {generateMutation.data && (
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-base">Generated Workflow</CardTitle>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleCopySchema(generateMutation.data.workflow.workflow_schema)}
                        >
                          {copiedId === 'schema' ? (
                            <>
                              <Check className="w-4 h-4 mr-1" />
                              Copied!
                            </>
                          ) : (
                            <>
                              <Copy className="w-4 h-4 mr-1" />
                              Copy Schema
                            </>
                          )}
                        </Button>
                        <Button
                          size="sm"
                          onClick={() => handleLoadToBuilder(generateMutation.data.workflow.workflow_schema)}
                        >
                          <Settings className="w-4 h-4 mr-1" />
                          Load to Builder
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* Workflow Info */}
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary">
                        {generateMutation.data.workflow.name}
                      </Badge>
                      <Badge variant="outline">
                        {generateMutation.data.workflow.status}
                      </Badge>
                    </div>

                    {/* Steps Preview */}
                    <div className="border rounded-lg p-4 bg-muted/50">
                      <h4 className="font-medium mb-2">Steps</h4>
                      <div className="space-y-1">
                        {generateMutation.data.workflow.workflow_schema.steps?.map(
                          (step, index) => (
                            <div
                              key={index}
                              className="flex items-center gap-2 text-sm"
                            >
                              <span className="w-5 h-5 rounded-full bg-primary/10 flex items-center justify-center text-xs">
                                {index + 1}
                              </span>
                              <span>{step.name}</span>
                              <span className="text-muted-foreground">
                                ({step.type})
                              </span>
                            </div>
                          )
                        )}
                      </div>
                    </div>

                    {/* Pattern Matches */}
                    {generateMutation.data.pattern_matches.length > 0 && (
                      <div>
                        <h4 className="font-medium mb-2">Detected Patterns</h4>
                        <div className="flex flex-wrap gap-2">
                          {generateMutation.data.pattern_matches.map((pattern) => (
                            <Badge key={pattern.id} variant="secondary">
                              {pattern.name}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Optimization Suggestions */}
                    {generateMutation.data.optimization_suggestions.length > 0 && (
                      <div>
                        <h4 className="font-medium mb-2">Optimization Suggestions</h4>
                        <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1">
                          {generateMutation.data.optimization_suggestions.map(
                            (suggestion, index) => (
                              <li key={index}>{suggestion}</li>
                            )
                          )}
                        </ul>
                      </div>
                    )}

                    {/* Matched Template */}
                    {generateMutation.data.matched_template && (
                      <div className="p-3 bg-primary/10 rounded-lg">
                        <div className="flex items-center gap-2">
                          <Sparkles className="w-4 h-4 text-primary" />
                          <span className="font-medium">
                            Matched Template: {generateMutation.data.matched_template.name}
                          </span>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              {/* Error State */}
              {generateMutation.isError && (
                <Card className="border-destructive">
                  <CardContent className="p-4">
                    <p className="text-destructive">
                      Failed to generate workflow. Please try again.
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>
          </ScrollArea>
        )}

        {/* Patterns Sidebar */}
        {patternsQuery.isSuccess && patternsQuery.data.patterns.length > 0 && (
          <div className="border-t border-border p-4">
            <h3 className="font-medium mb-3 flex items-center gap-2">
              <RefreshCw className="w-4 h-4" />
              Popular Patterns
            </h3>
            <div className="flex flex-wrap gap-2">
              {patternsQuery.data.patterns.slice(0, 6).map((pattern) => (
                <Badge
                  key={pattern.id}
                  variant="outline"
                  className="cursor-pointer hover:bg-accent"
                  onClick={() => handleQuickGenerate(
                    `Create a ${pattern.name} workflow that ${pattern.description || 'automates tasks'}`
                  )}
                >
                  {pattern.name}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AIWorkflowGenerator;
