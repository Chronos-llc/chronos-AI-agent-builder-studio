import React, { useState, useEffect } from 'react';
import {
    DashboardSummary,
    SystemHealthResponse,
    ActiveAlert,
    OptimizationRecommendation,
    SystemMetrics,
} from '../../types/systemOptimization';
import {
    getDashboardSummary,
    getSystemHealth,
    getMetrics,
} from '../../services/systemOptimizationService';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { ScrollArea } from '../ui/scroll-area';
import { Progress } from '../ui/progress';
import {
    Activity,
    AlertTriangle,
    CheckCircle,
    Clock,
    Cpu,
    Database,
    RefreshCw,
    TrendingUp,
    Zap,
    BarChart3,
    Bell,
    Lightbulb,
} from 'lucide-react';

// Simple KPI Card Component
function KPICard({
    title,
    value,
    unit,
    icon: Icon,
    trend,
    status,
}: {
    title: string;
    value: string | number;
    unit?: string;
    icon: React.ElementType;
    trend?: 'up' | 'down' | 'stable';
    status?: 'healthy' | 'warning' | 'critical';
}) {
    const statusColors = {
        healthy: 'border-green-500 bg-green-500/10',
        warning: 'border-yellow-500 bg-yellow-500/10',
        critical: 'border-red-500 bg-red-500/10',
    };

    const trendColors = {
        up: 'text-green-500',
        down: 'text-red-500',
        stable: 'text-gray-400',
    };

    return (
        <Card className={`border-l-4 ${statusColors[status || 'healthy']}`}>
            <CardContent className="p-4">
                <div className="flex items-center justify-between">
                    <div>
                        <p className="text-sm text-gray-400">{title}</p>
                        <p className="text-2xl font-bold mt-1">
                            {value}
                            {unit && <span className="text-sm font-normal text-gray-400 ml-1">{unit}</span>}
                        </p>
                        {trend && (
                            <p className={`text-xs mt-1 ${trendColors[trend]}`}>
                                {trend === 'up' && '↑ '}
                                {trend === 'down' && '↓ '}
                                {trend === 'stable' && '→ '}
                                {trend}
                            </p>
                        )}
                    </div>
                    <div className={`p-3 rounded-full ${status === 'critical' ? 'bg-red-500/20' :
                            status === 'warning' ? 'bg-yellow-500/20' : 'bg-green-500/20'
                        }`}>
                        <Icon className={`w-6 h-6 ${status === 'critical' ? 'text-red-500' :
                                status === 'warning' ? 'text-yellow-500' : 'text-green-500'
                            }`} />
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}

// Simple bar chart component for metrics
function SimpleBarChart({
    data,
    title,
}: {
    data: { label: string; value: number; color: string }[];
    title: string;
}) {
    const maxValue = Math.max(...data.map((d) => d.value), 1);

    return (
        <Card>
            <CardHeader>
                <CardTitle className="text-sm font-medium">{title}</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="space-y-2">
                    {data.map((item, index) => (
                        <div key={index} className="space-y-1">
                            <div className="flex justify-between text-xs">
                                <span>{item.label}</span>
                                <span>{item.value.toFixed(1)}%</span>
                            </div>
                            <Progress
                                value={(item.value / maxValue) * 100}
                                className="h-2 bg-gray-700"
                                indicatorClassName={item.color}
                            />
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
    );
}

// Health Status Card
function HealthStatusCard({ health }: { health: SystemHealthResponse }) {
    const statusConfig = {
        healthy: { icon: CheckCircle, color: 'text-green-500', bg: 'bg-green-500/10', label: 'Healthy' },
        degraded: { icon: AlertTriangle, color: 'text-yellow-500', bg: 'bg-yellow-500/10', label: 'Degraded' },
        unhealthy: { icon: AlertTriangle, color: 'text-red-500', bg: 'bg-red-500/10', label: 'Unhealthy' },
    };

    const config = statusConfig[health.status];
    const Icon = config.icon;

    return (
        <Card className={`border-2 ${config.bg}`}>
            <CardContent className="p-6">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <div className={`p-3 rounded-full ${config.bg}`}>
                            <Icon className={`w-8 h-8 ${config.color}`} />
                        </div>
                        <div>
                            <p className="text-sm text-gray-400">System Health</p>
                            <p className={`text-2xl font-bold ${config.color}`}>{config.label}</p>
                        </div>
                    </div>
                    <div className="text-right">
                        <p className="text-sm text-gray-400">Last Updated</p>
                        <p className="text-sm">{new Date(health.last_updated).toLocaleTimeString()}</p>
                    </div>
                </div>
                <div className="flex gap-4 mt-4 pt-4 border-t border-gray-700">
                    <Badge variant="outline" className="border-gray-600">
                        <Bell className="w-3 h-3 mr-1" />
                        {health.active_alerts} Active Alerts
                    </Badge>
                    <Badge variant="outline" className="border-gray-600">
                        <Lightbulb className="w-3 h-3 mr-1" />
                        {health.pending_recommendations} Recommendations
                    </Badge>
                </div>
            </CardContent>
        </Card>
    );
}

// Active Alerts List
function ActiveAlertsList({ alerts }: { alerts: ActiveAlert[] }) {
    const severityConfig = {
        LOW: { color: 'bg-blue-500', text: 'text-blue-400' },
        MEDIUM: { color: 'bg-yellow-500', text: 'text-yellow-400' },
        HIGH: { color: 'bg-orange-500', text: 'text-orange-400' },
        CRITICAL: { color: 'bg-red-500', text: 'text-red-400' },
    };

    if (alerts.length === 0) {
        return (
            <Card>
                <CardContent className="p-6 text-center text-gray-400">
                    <CheckCircle className="w-12 h-12 mx-auto mb-2 text-green-500" />
                    <p>No active alerts</p>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-yellow-500" />
                    Active Alerts ({alerts.length})
                </CardTitle>
            </CardHeader>
            <CardContent>
                <ScrollArea className="h-48">
                    <div className="space-y-2">
                        {alerts.map((alert, index) => (
                            <div
                                key={index}
                                className="p-3 border border-gray-700 rounded bg-gray-800/50"
                            >
                                <div className="flex items-center justify-between mb-1">
                                    <span className="font-medium">{alert.alert_rule_name}</span>
                                    <Badge className={`${severityConfig[alert.severity].color} text-white`}>
                                        {alert.severity}
                                    </Badge>
                                </div>
                                <div className="flex justify-between text-xs text-gray-400">
                                    <span>Triggered: {alert.triggered_value}</span>
                                    <span>{new Date(alert.triggered_at).toLocaleString()}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </ScrollArea>
            </CardContent>
        </Card>
    );
}

// Recommendations List
function RecommendationsList({ recommendations }: { recommendations: OptimizationRecommendation[] }) {
    const typeConfig = {
        PERFORMANCE: { icon: Zap, color: 'text-yellow-500' },
        COST: { icon: Database, color: 'text-green-500' },
        RELIABILITY: { icon: CheckCircle, color: 'text-blue-500' },
        SCALABILITY: { icon: TrendingUp, color: 'text-purple-500' },
    };

    const effortConfig = {
        LOW: 'bg-green-500/20 text-green-400',
        MEDIUM: 'bg-yellow-500/20 text-yellow-400',
        HIGH: 'bg-red-500/20 text-red-400',
    };

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <Lightbulb className="w-4 h-4 text-yellow-500" />
                    Top Recommendations
                </CardTitle>
            </CardHeader>
            <CardContent>
                <ScrollArea className="h-48">
                    <div className="space-y-2">
                        {recommendations.map((rec, index) => {
                            const type = typeConfig[rec.recommendation_type];
                            const Icon = type.icon;
                            return (
                                <div
                                    key={index}
                                    className="p-3 border border-gray-700 rounded bg-gray-800/50 hover:bg-gray-700/50 transition-colors"
                                >
                                    <div className="flex items-start justify-between gap-2">
                                        <div className="flex items-start gap-2">
                                            <Icon className={`w-4 h-4 mt-0.5 ${type.color}`} />
                                            <div>
                                                <p className="font-medium text-sm">{rec.title}</p>
                                                <p className="text-xs text-gray-400 mt-1 line-clamp-2">
                                                    {rec.description}
                                                </p>
                                            </div>
                                        </div>
                                        <Badge className={`${effortConfig[rec.effort_level]} text-xs`}>
                                            {rec.effort_level}
                                        </Badge>
                                    </div>
                                    <div className="flex items-center gap-2 mt-2">
                                        <Progress
                                            value={rec.impact_score * 100}
                                            className="flex-1 h-1 bg-gray-700"
                                            indicatorClassName="bg-blue-500"
                                        />
                                        <span className="text-xs text-gray-400">
                                            {Math.round(rec.impact_score * 100)}% impact
                                        </span>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </ScrollArea>
            </CardContent>
        </Card>
    );
}

export function OptimizationDashboard() {
    const [summary, setSummary] = useState<DashboardSummary | null>(null);
    const [health, setHealth] = useState<SystemHealthResponse | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [timeRange, setTimeRange] = useState('24h');
    const [metrics, setMetrics] = useState<SystemMetrics[]>([]);

    // Calculate time range based on selected option
    const getTimeRange = () => {
        const now = new Date();
        const endTime = now.toISOString();
        let startTime: Date;

        switch (timeRange) {
            case '1h':
                startTime = new Date(now.getTime() - 60 * 60 * 1000);
                break;
            case '24h':
                startTime = new Date(now.getTime() - 24 * 60 * 60 * 1000);
                break;
            case '7d':
                startTime = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
                break;
            case '30d':
                startTime = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
                break;
            default:
                startTime = new Date(now.getTime() - 24 * 60 * 60 * 1000);
        }

        return {
            startTime: startTime.toISOString(),
            endTime,
        };
    };

    const fetchData = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const [summaryData, healthData] = await Promise.all([
                getDashboardSummary(),
                getSystemHealth(),
            ]);
            setSummary(summaryData);
            setHealth(healthData);

            // Fetch metrics for charts with time range
            const { startTime, endTime } = getTimeRange();
            const metricsData = await getMetrics(undefined, undefined, startTime, endTime, 'avg', 20);
            setMetrics(metricsData);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
        // Auto-refresh every 30 seconds
        const interval = setInterval(fetchData, 30000);
        return () => clearInterval(interval);
    }, [timeRange]);

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="text-center">
                    <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-500" />
                    <p className="text-gray-400">Loading optimization dashboard...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="text-center text-red-500">
                    <AlertTriangle className="w-8 h-8 mx-auto mb-4" />
                    <p>{error}</p>
                    <Button onClick={fetchData} className="mt-4" variant="outline">
                        Retry
                    </Button>
                </div>
            </div>
        );
    }

    if (!summary || !health) {
        return null;
    }

    // Calculate KPIs from metrics
    const cpuMetrics = metrics.filter((m) => m.metric_type === 'CPU');
    const memoryMetrics = metrics.filter((m) => m.metric_type === 'MEMORY');
    const responseTimeMetrics = metrics.filter((m) => m.metric_type === 'RESPONSE_TIME');

    const avgCpu = cpuMetrics.length > 0
        ? cpuMetrics.reduce((sum, m) => sum + m.metric_value, 0) / cpuMetrics.length
        : 0;
    const avgMemory = memoryMetrics.length > 0
        ? memoryMetrics.reduce((sum, m) => sum + m.metric_value, 0) / memoryMetrics.length
        : 0;
    const avgResponseTime = responseTimeMetrics.length > 0
        ? responseTimeMetrics.reduce((sum, m) => sum + m.metric_value, 0) / responseTimeMetrics.length
        : 0;

    return (
        <div className="p-6 space-y-6 bg-gray-900 min-h-full">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold flex items-center gap-2">
                        <Activity className="w-6 h-6 text-blue-500" />
                        System Optimization Dashboard
                    </h1>
                    <p className="text-gray-400 mt-1">
                        Monitor performance metrics and optimization recommendations
                    </p>
                </div>
                <div className="flex items-center gap-4">
                    <Select value={timeRange} onValueChange={setTimeRange}>
                        <SelectTrigger className="w-40 bg-gray-800">
                            <SelectValue placeholder="Time Range" />
                        </SelectTrigger>
                        <SelectContent className="bg-gray-800">
                            <SelectItem value="1h">Last Hour</SelectItem>
                            <SelectItem value="24h">Last 24 Hours</SelectItem>
                            <SelectItem value="7d">Last 7 Days</SelectItem>
                            <SelectItem value="30d">Last 30 Days</SelectItem>
                        </SelectContent>
                    </Select>
                    <Button onClick={fetchData} variant="outline" size="sm">
                        <RefreshCw className="w-4 h-4 mr-2" />
                        Refresh
                    </Button>
                </div>
            </div>

            {/* Health Status */}
            <HealthStatusCard health={health} />

            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <KPICard
                    title="CPU Usage"
                    value={avgCpu.toFixed(1)}
                    unit="%"
                    icon={Cpu}
                    status={avgCpu > 80 ? 'critical' : avgCpu > 60 ? 'warning' : 'healthy'}
                    trend={avgCpu > 60 ? 'up' : 'stable'}
                />
                <KPICard
                    title="Memory Usage"
                    value={avgMemory.toFixed(1)}
                    unit="%"
                    icon={Database}
                    status={avgMemory > 80 ? 'critical' : avgMemory > 60 ? 'warning' : 'healthy'}
                />
                <KPICard
                    title="Avg Response Time"
                    value={avgResponseTime.toFixed(0)}
                    unit="ms"
                    icon={Clock}
                    status={avgResponseTime > 1000 ? 'critical' : avgResponseTime > 500 ? 'warning' : 'healthy'}
                />
                <KPICard
                    title="Active Alerts"
                    value={health.active_alerts}
                    icon={AlertTriangle}
                    status={health.active_alerts > 0 ? 'warning' : 'healthy'}
                />
            </div>

            {/* Charts and Lists */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Performance by Metric Type */}
                <SimpleBarChart
                    title="Resource Utilization"
                    data={[
                        { label: 'CPU', value: avgCpu, color: 'bg-blue-500' },
                        { label: 'Memory', value: avgMemory, color: 'bg-purple-500' },
                        { label: 'Response Time (scaled)', value: Math.min(avgResponseTime / 10, 100), color: 'bg-yellow-500' },
                    ]}
                />

                {/* Active Alerts */}
                <ActiveAlertsList alerts={summary.active_alerts} />
            </div>

            {/* Recommendations */}
            <RecommendationsList recommendations={summary.top_recommendations} />

            {/* Recent Metrics Table */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <BarChart3 className="w-4 h-4" />
                        Recent Metrics
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="border-b border-gray-700">
                                    <th className="text-left py-2 px-4 text-gray-400">Type</th>
                                    <th className="text-left py-2 px-4 text-gray-400">Name</th>
                                    <th className="text-right py-2 px-4 text-gray-400">Value</th>
                                    <th className="text-left py-2 px-4 text-gray-400">Unit</th>
                                    <th className="text-left py-2 px-4 text-gray-400">Timestamp</th>
                                </tr>
                            </thead>
                            <tbody>
                                {summary.recent_metrics.slice(0, 10).map((metric, index) => (
                                    <tr key={index} className="border-b border-gray-800 hover:bg-gray-800/50">
                                        <td className="py-2 px-4">
                                            <Badge variant="outline" className="border-gray-600">
                                                {metric.metric_type}
                                            </Badge>
                                        </td>
                                        <td className="py-2 px-4">{metric.metric_name}</td>
                                        <td className="py-2 px-4 text-right font-mono">
                                            {metric.metric_value.toFixed(2)}
                                        </td>
                                        <td className="py-2 px-4 text-gray-400">{metric.unit || '-'}</td>
                                        <td className="py-2 px-4 text-gray-400">
                                            {new Date(metric.timestamp).toLocaleString()}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}

export default OptimizationDashboard;