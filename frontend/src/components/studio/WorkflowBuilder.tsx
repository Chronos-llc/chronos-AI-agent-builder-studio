import React, { useState, useCallback } from 'react';
import { 
  Plus, Trash2, Edit, Play, Pause, 
  ArrowUp, ArrowDown, Copy, Settings, 
  Zap, GitBranch, Loader2
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { ScrollArea } from '../ui/scroll-area';
import type { WorkflowSchema, WorkflowStep } from '../../types/workflowGeneration';

interface WorkflowBuilderProps {
  initialSchema?: WorkflowSchema;
  onChange?: (schema: WorkflowSchema) => void;
  readOnly?: boolean;
}

const defaultSchema: WorkflowSchema = {
  name: 'New Workflow',
  description: '',
  steps: [],
  triggers: [{ type: 'manual', config: {} }],
};

export const WorkflowBuilder: React.FC<WorkflowBuilderProps> = ({
  initialSchema,
  onChange,
  readOnly = false,
}) => {
  const [schema, setSchema] = useState<WorkflowSchema>(initialSchema || defaultSchema);
  const [selectedStep, setSelectedStep] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [draggedStep, setDraggedStep] = useState<string | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);

  const handleSchemaChange = useCallback(
    (newSchema: WorkflowSchema) => {
      setSchema(newSchema);
      onChange?.(newSchema);
    },
    [onChange]
  );

  const handleStepAdd = () => {
    const newStep: WorkflowStep = {
      name: `Step ${schema.steps.length + 1}`,
      type: 'action',
      description: '',
    };
    const newSchema = {
      ...schema,
      steps: [...schema.steps, newStep],
    };
    handleSchemaChange(newSchema);
  };

  const handleStepUpdate = (stepName: string, updates: Partial<WorkflowStep>) => {
    const newSteps = schema.steps.map((step) =>
      step.name === stepName ? { ...step, ...updates } : step
    );
    handleSchemaChange({ ...schema, steps: newSteps });
  };

  const handleStepDelete = (stepName: string) => {
    const newSteps = schema.steps.filter((step) => step.name !== stepName);
    handleSchemaChange({ ...schema, steps: newSteps });
    if (selectedStep === stepName) {
      setSelectedStep(null);
    }
  };

  const handleStepMove = (stepName: string, direction: 'up' | 'down') => {
    const index = schema.steps.findIndex((step) => step.name === stepName);
    if (index === -1) return;

    const newSteps = [...schema.steps];
    const targetIndex = direction === 'up' ? index - 1 : index + 1;

    if (targetIndex < 0 || targetIndex >= newSteps.length) return;

    [newSteps[index], newSteps[targetIndex]] = [newSteps[targetIndex], newSteps[index]];
    handleSchemaChange({ ...schema, steps: newSteps });
  };

  const handleStepDuplicate = (stepName: string) => {
    const step = schema.steps.find((s) => s.name === stepName);
    if (!step) return;

    const newStep = { ...step, name: `${step.name} (copy)` };
    const index = schema.steps.findIndex((s) => s.name === stepName);
    const newSteps = [
      ...schema.steps.slice(0, index + 1),
      newStep,
      ...schema.steps.slice(index + 1),
    ];
    handleSchemaChange({ ...schema, steps: newSteps });
  };

  const handleDragStart = (e: React.DragEvent, stepName: string) => {
    setIsDragging(true);
    setDraggedStep(stepName);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = (e: React.DragEvent, targetStepName: string) => {
    e.preventDefault();
    setIsDragging(false);

    if (!draggedStep || draggedStep === targetStepName) return;

    const newSteps = [...schema.steps];
    const draggedIndex = newSteps.findIndex((s) => s.name === draggedStep);
    const targetIndex = newSteps.findIndex((s) => s.name === targetStepName);

    [newSteps[draggedIndex], newSteps[targetIndex]] = [
      newSteps[targetIndex],
      newSteps[draggedIndex],
    ];

    handleSchemaChange({ ...schema, steps: newSteps });
    setDraggedStep(null);
  };

  const handleExecuteWorkflow = async () => {
    setIsExecuting(true);
    // Simulate execution
    setTimeout(() => {
      setIsExecuting(false);
    }, 2000);
  };

  const getStepIcon = (type: string) => {
    switch (type) {
      case 'extract':
        return <GitBranch className="w-4 h-4 text-blue-500" />;
      case 'transform':
        return <Zap className="w-4 h-4 text-yellow-500" />;
      case 'load':
        return <ArrowDown className="w-4 h-4 text-green-500" />;
      default:
        return <Settings className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStepColor = (type: string) => {
    switch (type) {
      case 'extract':
        return 'border-l-blue-500 bg-blue-50';
      case 'transform':
        return 'border-l-yellow-500 bg-yellow-50';
      case 'load':
        return 'border-l-green-500 bg-green-50';
      case 'api_call':
        return 'border-l-purple-500 bg-purple-50';
      default:
        return 'border-l-gray-500 bg-gray-50';
    }
  };

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border">
        <div className="flex items-center gap-4">
          <Input
            value={schema.name}
            onChange={(e) => handleSchemaChange({ ...schema, name: e.target.value })}
            className="text-lg font-semibold bg-transparent border-none focus-visible:ring-0"
            placeholder="Workflow Name"
            disabled={readOnly}
          />
          <Badge variant="secondary">{schema.steps.length} steps</Badge>
          {schema.complexity && (
            <Badge variant="outline">{schema.complexity}</Badge>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleExecuteWorkflow}
            disabled={isExecuting || schema.steps.length === 0}
          >
            {isExecuting ? (
              <Loader2 className="w-4 h-4 animate-spin mr-2" />
            ) : (
              <Play className="w-4 h-4 mr-2" />
            )}
            Execute
          </Button>
          {!readOnly && (
            <Button size="sm" onClick={handleStepAdd}>
              <Plus className="w-4 h-4 mr-2" />
              Add Step
            </Button>
          )}
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Workflow Canvas */}
        <div className="flex-1 p-4 overflow-auto">
          <div className="max-w-2xl mx-auto">
            {/* Trigger */}
            <div className="mb-4">
              <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
                <span>Trigger</span>
              </div>
              <Card className="border-dashed border-2">
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                    <Zap className="w-4 h-4 text-primary" />
                  </div>
                  <div className="flex-1">
                    <span className="font-medium capitalize">{schema.triggers?.[0]?.type || 'manual'}</span>
                    <p className="text-sm text-muted-foreground">
                      {schema.triggers?.[0]?.type === 'schedule'
                        ? 'Runs on schedule'
                        : schema.triggers?.[0]?.type === 'webhook'
                        ? 'Webhook triggered'
                        : 'Manually started'}
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Steps */}
            <div className="space-y-2">
              {schema.steps.map((step, index) => (
                <div
                  key={step.name}
                  draggable={!readOnly}
                  onDragStart={(e) => handleDragStart(e, step.name)}
                  onDragOver={handleDragOver}
                  onDrop={(e) => handleDrop(e, step.name)}
                >
                  <Card
                    className={`cursor-pointer transition-all hover:shadow-md ${
                      selectedStep === step.name ? 'ring-2 ring-primary' : ''
                    } ${getStepColor(step.type)}`}
                    onClick={() => setSelectedStep(step.name)}
                  >
                    <CardContent className="p-4 flex items-center gap-3">
                      {/* Step Number / Drag Handle */}
                      <div className="flex items-center gap-2">
                        <span className="w-6 h-6 rounded-full bg-muted flex items-center justify-center text-xs font-medium">
                          {index + 1}
                        </span>
                        {getStepIcon(step.type)}
                      </div>

                      {/* Step Info */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-medium truncate">{step.name}</span>
                          <Badge variant="outline" className="text-xs">
                            {step.type}
                          </Badge>
                        </div>
                        {step.description && (
                          <p className="text-sm text-muted-foreground truncate">
                            {step.description}
                          </p>
                        )}
                      </div>

                      {/* Actions */}
                      {!readOnly && (
                        <div className="flex items-center gap-1">
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleStepMove(step.name, 'up');
                            }}
                            disabled={index === 0}
                          >
                            <ArrowUp className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleStepMove(step.name, 'down');
                            }}
                            disabled={index === schema.steps.length - 1}
                          >
                            <ArrowDown className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleStepDuplicate(step.name);
                            }}
                          >
                            <Copy className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 text-destructive"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleStepDelete(step.name);
                            }}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      )}
                    </CardContent>
                  </Card>

                  {/* Connector Line */}
                  {index < schema.steps.length - 1 && (
                    <div className="flex justify-center py-1">
                      <div className="w-0.5 h-4 bg-border" />
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Add Step Placeholder */}
            {!readOnly && schema.steps.length > 0 && (
              <div className="mt-4">
                <div className="flex justify-center py-1">
                  <div className="w-0.5 h-4 bg-border" />
                </div>
                <Button
                  variant="outline"
                  className="w-full border-dashed"
                  onClick={handleStepAdd}
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Step
                </Button>
              </div>
            )}

            {/* Empty State */}
            {schema.steps.length === 0 && (
              <Card className="border-dashed border-2">
                <CardContent className="p-8 text-center">
                  <Zap className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
                  <h3 className="font-medium mb-2">No steps yet</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Add your first step to build the workflow
                  </p>
                  {!readOnly && (
                    <Button onClick={handleStepAdd}>
                      <Plus className="w-4 h-4 mr-2" />
                      Add First Step
                    </Button>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        </div>

        {/* Step Properties Panel */}
        {selectedStep && (
          <div className="w-80 border-l border-border bg-card">
            <div className="p-4 border-b border-border">
              <h3 className="font-semibold">Step Properties</h3>
            </div>
            <ScrollArea className="h-[calc(100%-60px)]">
              <div className="p-4 space-y-4">
                {(() => {
                  const step = schema.steps.find((s) => s.name === selectedStep);
                  if (!step) return null;

                  return (
                    <>
                      <div>
                        <label className="block text-sm font-medium mb-1">Name</label>
                        <Input
                          value={step.name}
                          onChange={(e) =>
                            handleStepUpdate(step.name, { name: e.target.value })
                          }
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-1">Type</label>
                        <select
                          value={step.type}
                          onChange={(e) =>
                            handleStepUpdate(step.name, { type: e.target.value })
                          }
                          className="w-full px-3 py-2 border border-input rounded-md bg-background"
                        >
                          <option value="start">Start</option>
                          <option value="extract">Extract</option>
                          <option value="transform">Transform</option>
                          <option value="load">Load</option>
                          <option value="api_call">API Call</option>
                          <option value="action">Action</option>
                          <option value="notification">Notification</option>
                          <option value="end">End</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-1">Description</label>
                        <textarea
                          value={step.description || ''}
                          onChange={(e) =>
                            handleStepUpdate(step.name, { description: e.target.value })
                          }
                          className="w-full px-3 py-2 border border-input rounded-md bg-background min-h-[80px]"
                          placeholder="Describe what this step does"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-1">Depends On</label>
                        <select
                          multiple
                          value={step.depends_on || []}
                          onChange={(e) => {
                            const values = Array.from(
                              e.target.selectedOptions,
                              (option) => option.value
                            );
                            handleStepUpdate(step.name, { depends_on: values });
                          }}
                          className="w-full px-3 py-2 border border-input rounded-md bg-background min-h-[100px]"
                        >
                          {schema.steps
                            .filter((s) => s.name !== step.name)
                            .map((s) => (
                              <option key={s.name} value={s.name}>
                                {s.name}
                              </option>
                            ))}
                        </select>
                      </div>
                    </>
                  );
                })()}
              </div>
            </ScrollArea>
          </div>
        )}
      </div>
    </div>
  );
};

export default WorkflowBuilder;
