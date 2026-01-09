import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  RefreshCw, TrendingUp, Zap, BarChart3,
  ChevronRight, Info, Loader2, AlertCircle
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { ScrollArea } from '../ui/scroll-area';
import { Progress } from '../ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { workflowGenerationService } from '../../services/workflowGenerationService';
import type { WorkflowPattern, WorkflowSchema } from '../../types/workflowGeneration';

interface PatternVisualizerProps {
  currentSchema?: WorkflowSchema;
  onPatternSelect?: (pattern: WorkflowPattern) => void;
  onApplyPattern?: (pattern: WorkflowPattern) => void;
}

export const PatternVisualizer: React.FC<PatternVisualizerProps> = ({
  currentSchema,
  onPatternSelect,
  onApplyPattern,
}) => {
  const [selectedPattern, setSelectedPattern] = useState<WorkflowPattern | null>(null);
  const [activeTab, setActiveTab] = useState('patterns');

  const { data: patternsData, isLoading, error, refetch } = useQuery({
    queryKey: ['workflow-patterns'],
    queryFn: () => workflowGenerationService.listPatterns(),
    staleTime: 30000, // Cache for 30 seconds
  });

  const { data: recognitionData, isLoading: isRecognizing } = useQuery({
    queryKey: ['pattern-recognition', currentSchema],
    queryFn: () => 
      currentSchema 
        ? workflowGenerationService.recognizePattern(currentSchema)
        : Promise.resolve(null),
    enabled: !!currentSchema,
  });

  const handlePatternSelect = (pattern: WorkflowPattern) => {
    setSelectedPattern(pattern);
    onPatternSelect?.(pattern);
  };

  const handleApplyPattern = (pattern: WorkflowPattern) => {
    onApplyPattern?.(pattern);
  };

  const getSuccessRateColor = (rate: number) => {
    if (rate >= 0.9) return 'text-green-500';
    if (rate >= 0.7) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getSuccessRateLabel = (rate: number) => {
    if (rate >= 0.9) return 'Excellent';
    if (rate >= 0.7) return 'Good';
    if (rate >= 0.5) return 'Fair';
    return 'Needs Improvement';
  };

  const formatUsageCount = (count: number) => {
    if (count >= 1000) {
      return `${(count / 1000).toFixed(1)}k`;
    }
    return count.toString();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="flex flex-col items-center gap-2">
          <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
          <span className="text-sm text-muted-foreground">Loading patterns...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="flex flex-col items-center gap-2 text-center p-4">
          <AlertCircle className="w-8 h-8 text-destructive" />
          <span className="text-sm text-destructive">Failed to load patterns</span>
          <Button variant="outline" size="sm" onClick={() => refetch()}>
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  const patterns = patternsData?.patterns || [];
  const matchedPattern = recognitionData?.matched_pattern;

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border">
        <div className="flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-primary" />
          <h2 className="font-semibold">Pattern Visualizer</h2>
        </div>
        <Button variant="outline" size="sm" onClick={() => refetch()}>
          <RefreshCw className={`w-4 h-4 mr-1 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      <div className="flex-1 overflow-hidden flex flex-col">
        <ScrollArea className="flex-1">
          <div className="p-4 space-y-4">
            {/* Current Schema Analysis */}
            {currentSchema && (
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-base flex items-center gap-2">
                    <Zap className="w-4 h-4" />
                    Current Schema Analysis
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {isRecognizing ? (
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Analyzing schema...
                    </div>
                  ) : matchedPattern ? (
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <Badge variant="secondary">
                          {matchedPattern.name}
                        </Badge>
                        <span className="text-sm text-muted-foreground">
                          {((recognitionData?.confidence || 0) * 100).toFixed(0)}% match
                        </span>
                      </div>
                      <div className="text-sm">
                        {matchedPattern.description || `Detected ${matchedPattern.name} pattern in your workflow.`}
                      </div>
                    </div>
                  ) : (
                    <div className="text-sm text-muted-foreground">
                      No matching patterns detected in current schema.
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Pattern Tabs */}
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="w-full">
                <TabsTrigger value="patterns" className="flex-1">
                  All Patterns
                </TabsTrigger>
                <TabsTrigger value="popular" className="flex-1">
                  Popular
                </TabsTrigger>
                <TabsTrigger value="recommended" className="flex-1">
                  Recommended
                </TabsTrigger>
              </TabsList>

              <TabsContent value="patterns" className="mt-4 space-y-2">
                {patterns.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    <BarChart3 className="w-8 h-8 mx-auto mb-2" />
                    <p>No patterns available</p>
                  </div>
                ) : (
                  patterns.map((pattern) => (
                    <PatternCard
                      key={pattern.id}
                      pattern={pattern}
                      isSelected={selectedPattern?.id === pattern.id}
                      onSelect={() => handlePatternSelect(pattern)}
                      onApply={() => handleApplyPattern(pattern)}
                      getSuccessRateColor={getSuccessRateColor}
                      getSuccessRateLabel={getSuccessRateLabel}
                      formatUsageCount={formatUsageCount}
                    />
                  ))
                )}
              </TabsContent>

              <TabsContent value="popular" className="mt-4 space-y-2">
                {patterns
                  .sort((a, b) => b.usage_count - a.usage_count)
                  .slice(0, 5)
                  .map((pattern) => (
                    <PatternCard
                      key={pattern.id}
                      pattern={pattern}
                      isSelected={selectedPattern?.id === pattern.id}
                      onSelect={() => handlePatternSelect(pattern)}
                      onApply={() => handleApplyPattern(pattern)}
                      getSuccessRateColor={getSuccessRateColor}
                      getSuccessRateLabel={getSuccessRateLabel}
                      formatUsageCount={formatUsageCount}
                    />
                  ))}
              </TabsContent>

              <TabsContent value="recommended" className="mt-4 space-y-2">
                {patterns
                  .filter((p) => p.success_rate >= 0.8)
                  .sort((a, b) => b.success_rate - a.success_rate)
                  .slice(0, 5)
                  .map((pattern) => (
                    <PatternCard
                      key={pattern.id}
                      pattern={pattern}
                      isSelected={selectedPattern?.id === pattern.id}
                      onSelect={() => handlePatternSelect(pattern)}
                      onApply={() => handleApplyPattern(pattern)}
                      getSuccessRateColor={getSuccessRateColor}
                      getSuccessRateLabel={getSuccessRateLabel}
                      formatUsageCount={formatUsageCount}
                    />
                  ))}
              </TabsContent>
            </Tabs>

            {/* Pattern Stats */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base flex items-center gap-2">
                  <TrendingUp className="w-4 h-4" />
                  Statistics
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold">{patterns.length}</div>
                    <div className="text-xs text-muted-foreground">Total Patterns</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold">
                      {patterns.reduce((acc, p) => acc + p.usage_count, 0)}
                    </div>
                    <div className="text-xs text-muted-foreground">Total Uses</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold">
                      {patterns.filter((p) => p.success_rate >= 0.8).length}
                    </div>
                    <div className="text-xs text-muted-foreground">High Success</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold">
                      {(
                        patterns.reduce((acc, p) => acc + p.success_rate, 0) /
                        (patterns.length || 1)
                      ).toFixed(1)}
                    </div>
                    <div className="text-xs text-muted-foreground">Avg Success Rate</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </ScrollArea>

        {/* Selected Pattern Details */}
        {selectedPattern && (
          <div className="border-t border-border p-4 bg-muted/30">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium">{selectedPattern.name}</h4>
              <Button size="sm" onClick={() => handleApplyPattern(selectedPattern)}>
                Apply Pattern
              </Button>
            </div>
            <p className="text-sm text-muted-foreground mb-3">
              {selectedPattern.description || 'No description available.'}
            </p>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span>Success Rate</span>
                <span className={getSuccessRateColor(selectedPattern.success_rate)}>
                  {(selectedPattern.success_rate * 100).toFixed(0)}%
                </span>
              </div>
              <Progress value={selectedPattern.success_rate * 100} className="h-2" />
              <div className="flex items-center justify-between text-sm">
                <span>Usage Count</span>
                <span>{formatUsageCount(selectedPattern.usage_count)} uses</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Pattern Card Component
interface PatternCardProps {
  pattern: WorkflowPattern;
  isSelected: boolean;
  onSelect: () => void;
  onApply: () => void;
  getSuccessRateColor: (rate: number) => string;
  getSuccessRateLabel: (rate: number) => string;
  formatUsageCount: (count: number) => string;
}

const PatternCard: React.FC<PatternCardProps> = ({
  pattern,
  isSelected,
  onSelect,
  onApply,
  getSuccessRateColor,
  getSuccessRateLabel,
  formatUsageCount,
}) => {
  return (
    <Card
      className={`cursor-pointer transition-all hover:shadow-md ${
        isSelected ? 'ring-2 ring-primary' : ''
      }`}
      onClick={onSelect}
    >
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h4 className="font-medium truncate">{pattern.name}</h4>
              <Badge variant="outline" className="text-xs">
                {getSuccessRateLabel(pattern.success_rate)}
              </Badge>
            </div>
            {pattern.description && (
              <p className="text-sm text-muted-foreground line-clamp-2">
                {pattern.description}
              </p>
            )}
          </div>
          <ChevronRight className={`w-4 h-4 ml-2 ${
            isSelected ? 'text-primary' : 'text-muted-foreground'
          }`} />
        </div>
        <div className="flex items-center gap-4 mt-3">
          <div className="flex items-center gap-1 text-sm">
            <TrendingUp className={`w-4 h-4 ${getSuccessRateColor(pattern.success_rate)}`} />
            <span className={getSuccessRateColor(pattern.success_rate)}>
              {(pattern.success_rate * 100).toFixed(0)}%
            </span>
          </div>
          <div className="flex items-center gap-1 text-sm text-muted-foreground">
            <Zap className="w-4 h-4" />
            <span>{formatUsageCount(pattern.usage_count)} uses</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default PatternVisualizer;
