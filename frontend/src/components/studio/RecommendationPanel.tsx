import { useState, useEffect } from 'react';
import {
  OptimizationRecommendation,
  RecommendationType,
  RecommendationStatus,
} from '../../types/systemOptimization';
import {
  listRecommendations,
  applyRecommendation,
  generateRecommendations,
  updateRecommendationStatus,
} from '../../services/systemOptimizationService';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Badge } from '../ui/badge';
import { Input } from '../ui/input';
import {
  Lightbulb,
  CheckCircle,
  XCircle,
  Clock,
  Zap,
  DollarSign,
  Shield,
  Scale,
  RefreshCw,
  ChevronDown,
  ChevronUp,
  Sparkles,
  AlertTriangle,
} from 'lucide-react';
import toast from 'react-hot-toast';
import './RecommendationPanel.css';

interface RecommendationPanelProps {
  agentId?: number;
}

export function RecommendationPanel({ agentId }: RecommendationPanelProps) {
  const [recommendations, setRecommendations] = useState<OptimizationRecommendation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [filterType, setFilterType] = useState<RecommendationType | 'ALL'>('ALL');
  const [filterStatus, setFilterStatus] = useState<RecommendationStatus | 'ALL'>('ALL');
  const [filterImpactMin, setFilterImpactMin] = useState(0);
  const [isGenerating, setIsGenerating] = useState(false);

  const fetchRecommendations = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await listRecommendations(
        agentId,
        filterType !== 'ALL' ? filterType : undefined,
        filterStatus !== 'ALL' ? filterStatus : undefined,
        filterImpactMin > 0 ? filterImpactMin : undefined
      );
      setRecommendations(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load recommendations');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [agentId, filterType, filterStatus, filterImpactMin]);

  const handleApply = async (recommendation: OptimizationRecommendation) => {
    try {
      await applyRecommendation(recommendation.id, { apply_changes: true, auto_approve: false });
      toast.success(`Applied recommendation: ${recommendation.title}`);
      fetchRecommendations();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to apply recommendation');
    }
  };

  const handleDismiss = async (recommendation: OptimizationRecommendation) => {
    try {
      await updateRecommendationStatus(recommendation.id, 'DISMISSED');
      toast.success('Recommendation dismissed');
      fetchRecommendations();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to dismiss recommendation');
    }
  };

  const handleGenerate = async () => {
    if (!agentId) {
      toast.error('Agent ID required to generate recommendations');
      return;
    }

    setIsGenerating(true);
    try {
      const result = await generateRecommendations(agentId);
      toast.success(`Generated ${result.recommendations_count} recommendations`);
      fetchRecommendations();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to generate recommendations');
    } finally {
      setIsGenerating(false);
    }
  };

  const getTypeConfig = (type: RecommendationType) => {
    const configs = {
      PERFORMANCE: { icon: Zap, color: 'text-yellow-500', bg: 'bg-yellow-500/10', border: 'border-yellow-500' },
      COST: { icon: DollarSign, color: 'text-green-500', bg: 'bg-green-500/10', border: 'border-green-500' },
      RELIABILITY: { icon: Shield, color: 'text-blue-500', bg: 'bg-blue-500/10', border: 'border-blue-500' },
      SCALABILITY: { icon: Scale, color: 'text-purple-500', bg: 'bg-purple-500/10', border: 'border-purple-500' },
    };
    return configs[type];
  };

  const getStatusConfig = (status: RecommendationStatus) => {
    const configs = {
      PENDING: { icon: Clock, color: 'text-gray-400', bg: 'bg-gray-500/10', label: 'Pending' },
      APPLIED: { icon: CheckCircle, color: 'text-green-500', bg: 'bg-green-500/10', label: 'Applied' },
      DISMISSED: { icon: XCircle, color: 'text-red-500', bg: 'bg-red-500/10', label: 'Dismissed' },
      EXPIRED: { icon: AlertTriangle, color: 'text-orange-500', bg: 'bg-orange-500/10', label: 'Expired' },
    };
    return configs[status];
  };

  const getEffortConfig = (effort: string) => {
    const configs = {
      LOW: { color: 'bg-green-500', label: 'Low Effort', barWidthClass: 'recommendation-effort-bar--low' },
      MEDIUM: { color: 'bg-yellow-500', label: 'Medium Effort', barWidthClass: 'recommendation-effort-bar--medium' },
      HIGH: { color: 'bg-red-500', label: 'High Effort', barWidthClass: 'recommendation-effort-bar--high' },
    };
    return configs[effort as keyof typeof configs];
  };

  const getImpactWidth = (impactScore: number) => {
    return `${Math.round(impactScore * 100)}%`;
  };

  const filteredRecommendations = recommendations.filter((r) => {
    if (filterType !== 'ALL' && r.recommendation_type !== filterType) return false;
    if (filterStatus !== 'ALL' && r.status !== filterStatus) return false;
    if (r.impact_score < filterImpactMin) return false;
    return true;
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-500" />
          <p className="text-gray-400">Loading recommendations...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center text-red-500">
          <p>{error}</p>
          <Button onClick={fetchRecommendations} className="mt-4" variant="outline">
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with filters and actions */}
      <div className="flex flex-wrap items-center gap-4">
        <div className="flex items-center gap-2">
          <Lightbulb className="w-5 h-5 text-yellow-500" />
          <h2 className="text-xl font-bold">Optimization Recommendations</h2>
        </div>
        <div className="flex-1" />
        <Button
          onClick={handleGenerate}
          disabled={!agentId || isGenerating}
          variant="outline"
          size="sm"
        >
          <Sparkles className={`w-4 h-4 mr-2 ${isGenerating ? 'animate-spin' : ''}`} />
          Generate AI Recommendations
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-4 p-4 bg-gray-800 rounded-lg border border-gray-700">
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-400">Type:</span>
          <Select
            value={filterType}
            onValueChange={(v) => setFilterType(v as RecommendationType | 'ALL')}
          >
            <SelectTrigger className="w-36 bg-gray-700">
              <SelectValue placeholder="All Types" />
            </SelectTrigger>
            <SelectContent className="bg-gray-800">
              <SelectItem value="ALL">All Types</SelectItem>
              <SelectItem value="PERFORMANCE">Performance</SelectItem>
              <SelectItem value="COST">Cost</SelectItem>
              <SelectItem value="RELIABILITY">Reliability</SelectItem>
              <SelectItem value="SCALABILITY">Scalability</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-400">Status:</span>
          <Select
            value={filterStatus}
            onValueChange={(v) => setFilterStatus(v as RecommendationStatus | 'ALL')}
          >
            <SelectTrigger className="w-36 bg-gray-700">
              <SelectValue placeholder="All Status" />
            </SelectTrigger>
            <SelectContent className="bg-gray-800">
              <SelectItem value="ALL">All Status</SelectItem>
              <SelectItem value="PENDING">Pending</SelectItem>
              <SelectItem value="APPLIED">Applied</SelectItem>
              <SelectItem value="DISMISSED">Dismissed</SelectItem>
              <SelectItem value="EXPIRED">Expired</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-400">Min Impact:</span>
          <Input
            type="number"
            min="0"
            max="1"
            step="0.1"
            value={filterImpactMin}
            onChange={(e) => setFilterImpactMin(parseFloat(e.target.value) || 0)}
            className="w-24 bg-gray-700"
          />
        </div>

        <div className="flex-1" />

        <Badge variant="outline" className="border-gray-600">
          {filteredRecommendations.length} recommendations
        </Badge>
      </div>

      {/* Recommendations List */}
      {filteredRecommendations.length === 0 ? (
        <Card>
          <CardContent className="p-8 text-center">
            <Lightbulb className="w-12 h-12 mx-auto mb-4 text-gray-600" />
            <p className="text-gray-400">No recommendations found matching your filters</p>
            {agentId && (
              <Button onClick={handleGenerate} className="mt-4" variant="outline">
                <Sparkles className="w-4 h-4 mr-2" />
                Generate Recommendations
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {filteredRecommendations.map((recommendation) => {
            const typeConfig = getTypeConfig(recommendation.recommendation_type);
            const statusConfig = getStatusConfig(recommendation.status);
            const effortConfig = getEffortConfig(recommendation.effort_level);
            const isExpanded = expandedId === recommendation.id;

            return (
              <Card
                key={recommendation.id}
                className={`border-l-4 ${typeConfig.bg} ${typeConfig.border}`}
              >
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                      <div className={`p-2 rounded-lg ${typeConfig.bg}`}>
                        <typeConfig.icon className={`w-5 h-5 ${typeConfig.color}`} />
                      </div>
                      <div>
                        <CardTitle className="text-lg">{recommendation.title}</CardTitle>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge className={`${typeConfig.bg} ${typeConfig.color} border-0`}>
                            {recommendation.recommendation_type}
                          </Badge>
                          <Badge className={`${statusConfig.bg} ${statusConfig.color} border-0`}>
                            <statusConfig.icon className="w-3 h-3 mr-1" />
                            {statusConfig.label}
                          </Badge>
                          <Badge variant="outline" className="border-gray-600">
                            {effortConfig.label}
                          </Badge>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="text-right">
                        <p className="text-sm text-gray-400">Impact Score</p>
                        <p className="text-xl font-bold text-blue-500">
                          {Math.round((recommendation.impact_score ?? 0) * 100)}%
                        </p>
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-300 mb-4">{recommendation.description}</p>

                  {/* Impact bar */}
                  <div className="mb-4">
                    <div className="flex justify-between text-xs text-gray-400 mb-1">
                      <span>Impact</span>
                      <span>Effort</span>
                    </div>
                    <div className="flex gap-1">
                       <div className="flex-1 bg-gray-700 rounded-full h-2 overflow-hidden">
                        <div
                          className="bg-blue-500 h-2 rounded-full transition-all recommendation-impact-bar"
                          style={{ width: getImpactWidth(recommendation.impact_score ?? 0) }}
                        />
                      </div>
                      <div className="w-20 bg-gray-700 rounded-full h-2 overflow-hidden">
                        <div
                          className={`${effortConfig.color} h-2 rounded-full transition-all recommendation-effort-bar ${effortConfig.barWidthClass}`}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Current and recommended values */}
                  {(recommendation.current_value || recommendation.recommended_value) && (
                    <div className="grid grid-cols-2 gap-4 p-3 bg-gray-800 rounded-lg mb-4">
                      <div>
                        <p className="text-xs text-gray-400">Current Value</p>
                        <p className="font-mono">{recommendation.current_value || '-'}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-400">Recommended Value</p>
                        <p className="font-mono text-green-500">{recommendation.recommended_value || '-'}</p>
                      </div>
                    </div>
                  )}

                  {/* Expandable details */}
                  {isExpanded && (
                    <div className="p-4 bg-gray-800 rounded-lg mb-4">
                      <h4 className="font-medium mb-2">Additional Details</h4>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="text-gray-400">Created</p>
                          <p>{new Date(recommendation.created_at).toLocaleString()}</p>
                        </div>
                        {recommendation.expires_at && (
                          <div>
                            <p className="text-gray-400">Expires</p>
                            <p>{new Date(recommendation.expires_at).toLocaleString()}</p>
                          </div>
                        )}
                        {recommendation.agent_id && (
                          <div>
                            <p className="text-gray-400">Agent ID</p>
                            <p>{recommendation.agent_id}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Actions */}
                  {recommendation.status === 'PENDING' && (
                    <div className="flex gap-2">
                      <Button
                        onClick={() => handleApply(recommendation)}
                        className="bg-green-600 hover:bg-green-700"
                      >
                        <CheckCircle className="w-4 h-4 mr-2" />
                        Apply
                      </Button>
                      <Button
                        onClick={() => handleDismiss(recommendation)}
                        variant="outline"
                      >
                        <XCircle className="w-4 h-4 mr-2" />
                        Dismiss
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setExpandedId(isExpanded ? null : recommendation.id)}
                      >
                        {isExpanded ? (
                          <>
                            <ChevronUp className="w-4 h-4 mr-2" />
                            Less
                          </>
                        ) : (
                          <>
                            <ChevronDown className="w-4 h-4 mr-2" />
                            More
                          </>
                        )}
                      </Button>
                    </div>
                  )}

                  {recommendation.status !== 'PENDING' && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setExpandedId(isExpanded ? null : recommendation.id)}
                    >
                      {isExpanded ? (
                        <>
                          <ChevronUp className="w-4 h-4 mr-2" />
                          Less
                        </>
                      ) : (
                        <>
                          <ChevronDown className="w-4 h-4 mr-2" />
                          More
                        </>
                      )}
                    </Button>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default RecommendationPanel;