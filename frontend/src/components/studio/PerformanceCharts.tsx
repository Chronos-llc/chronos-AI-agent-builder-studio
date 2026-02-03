import { useState, useEffect } from 'react';
import {
  TimeSeriesDataPoint,
  MetricType,
  AggregationType,
} from '../../types/systemOptimization';
import {
  getMetrics,
} from '../../services/systemOptimizationService';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';

import {
  RefreshCw,
  Download,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Filter,
  BarChart3,
  TrendingUp,
  Activity,
  LineChart as LineChartIcon,
} from 'lucide-react';

// Custom simple chart components since recharts isn't installed
function SimpleLineChart({
  data,
  strokeColor = '#3b82f6',
  height = 300,
}: {
  data: TimeSeriesDataPoint[];
  strokeColor?: string;
  height?: number;
}) {
  const maxValue = Math.max(...data.map((d) => d.value), 1);
  const minValue = Math.min(...data.map((d) => d.value), 0);

  return (
    <div className={`w-full h-[${height}px]`}>
      <svg width="100%" height="100%" className="overflow-visible">
        {/* Grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map((tick) => (
          <line
            key={tick}
            x1="0"
            y1={height - tick * height}
            x2="100%"
            y2={height - tick * height}
            stroke="#374151"
            strokeDasharray="4"
            strokeWidth="1"
          />
        ))}

        {/* Data line */}
        <polyline
          fill="none"
          stroke={strokeColor}
          strokeWidth="2"
          points={data
            .map((d, i) => {
              const x = (i / (data.length - 1)) * 100;
              const y = height - ((d.value - minValue) / (maxValue - minValue || 1)) * height;
              return `${x}%,${y}`;
            })
            .join(' ')}
        />

        {/* Data points */}
        {data.map((d, i) => {
          const x = (i / (data.length - 1)) * 100;
          const y = height - ((d.value - minValue) / (maxValue - minValue || 1)) * height;
          return (
            <circle
              key={i}
              cx={`${x}%`}
              cy={y}
              r="4"
              fill={strokeColor}
              stroke="#1f2937"
              strokeWidth="2"
              className="cursor-pointer hover:scale-125 transition-all"
            >
              <title>
                {new Date(d.timestamp).toLocaleString()}: {d.value}
              </title>
            </circle>
          );
        })}

        {/* X-axis labels */}
        {data.filter((_, i) => i % Math.ceil(data.length / 5) === 0).map((d, i) => {
          const x = (i * Math.ceil(data.length / 5) / (data.length - 1)) * 100;
          return (
            <text
              key={i}
              x={`${x}%`}
              y={height + 20}
              textAnchor="middle"
              fill="#9ca3af"
              fontSize="12"
            >
              {new Date(d.timestamp).toLocaleTimeString()}
            </text>
          );
        })}

        {/* Y-axis labels */}
        {[0, 0.25, 0.5, 0.75, 1].map((tick) => (
          <text
            key={tick}
            x="-10"
            y={height - tick * height + 4}
            textAnchor="end"
            fill="#9ca3af"
            fontSize="12"
          >
            {((maxValue - minValue) * tick + minValue).toFixed(1)}
          </text>
        ))}
      </svg>
    </div>
  );
}

// Simple bar chart component
function SimpleBarChart({
  data,
  height = 300,
}: {
  data: { name: string; value: number; color: string }[];
  height?: number;
}) {
  const maxValue = Math.max(...data.map((d) => d.value), 1);

  return (
    <div className={`w-full h-[${height}px]`}>
      <svg id="comparison-chart" width="100%" height="100%" className="overflow-visible">
        {/* Grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map((tick) => (
          <line
            key={tick}
            x1="0"
            y1={height - tick * height}
            x2="100%"
            y2={height - tick * height}
            stroke="#374151"
            strokeDasharray="4"
            strokeWidth="1"
          />
        ))}

        {/* Bars */}
        {data.map((d, i) => {
          const barWidth = 80 / data.length;
          const x = 10 + i * (90 / data.length);
          const barHeight = (d.value / maxValue) * (height - 40);
          const y = height - barHeight - 20;

          return (
            <g key={i}>
              <rect
                x={`${x}%`}
                y={y}
                width={`${barWidth}%`}
                height={barHeight}
                fill={d.color}
                rx="4"
                className="cursor-pointer hover:opacity-80 transition-opacity"
              >
                <title>{d.name}: {d.value.toFixed(2)}</title>
              </rect>
              <text
                x={`${x + barWidth / 2}%`}
                y={height - 5}
                textAnchor="middle"
                fill="#9ca3af"
                fontSize="10"
              >
                {d.name}
              </text>
            </g>
          );
        })}

        {/* Y-axis labels */}
        {[0, 0.25, 0.5, 0.75, 1].map((tick) => (
          <text
            key={tick}
            x="-10"
            y={height - tick * height + 4}
            textAnchor="end"
            fill="#9ca3af"
            fontSize="12"
          >
            {((maxValue) * tick).toFixed(1)}
          </text>
        ))}
      </svg>
    </div>
  );
}

// Export chart as image
function exportChartAsImage(elementId: string, filename: string) {
  const element = document.getElementById(elementId);
  if (!element) return;

  // Create a canvas from the SVG
  const svgData = new XMLSerializer().serializeToString(element);
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  const img = new Image();

  canvas.width = element.offsetWidth * 2;
  canvas.height = element.offsetHeight * 2;

  img.onload = () => {
    if (ctx) {
      ctx.fillStyle = '#111827';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

      const a = document.createElement('a');
      a.download = `${filename}.png`;
      a.href = canvas.toDataURL('image/png');
      a.click();
    }
  };

  img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgData)));
}

interface PerformanceChartsProps {
  agentId?: number;
  defaultMetricType?: MetricType;
}

export function PerformanceCharts({ agentId, defaultMetricType }: PerformanceChartsProps) {
  const [metricType, setMetricType] = useState<MetricType>(
    defaultMetricType || 'CPU'
  );
  const [aggregation, setAggregation] = useState<AggregationType>('avg');
  const [timeRange, setTimeRange] = useState('24h');
  const [isLoading, setIsLoading] = useState(true);
  const [chartData, setChartData] = useState<TimeSeriesDataPoint[]>([]);
  const [comparisonData, setComparisonData] = useState<{
    CPU: number;
    MEMORY: number;
    DISK: number;
    NETWORK: number;
    RESPONSE_TIME: number;
    THROUGHPUT: number;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [zoomLevel, setZoomLevel] = useState(1);

  const timeRanges = {
    '1h': { start: new Date(Date.now() - 60 * 60 * 1000), end: new Date() },
    '6h': { start: new Date(Date.now() - 6 * 60 * 60 * 1000), end: new Date() },
    '24h': { start: new Date(Date.now() - 24 * 60 * 60 * 1000), end: new Date() },
    '7d': { start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), end: new Date() },
    '30d': { start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), end: new Date() },
  };

  const fetchData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const { start, end } = timeRanges[timeRange as keyof typeof timeRanges];

      // Fetch main metric data
      const metrics = await getMetrics(
        metricType,
        undefined,
        start.toISOString(),
        end.toISOString(),
        aggregation,
        100,
        agentId
      );

      const dataPoints: TimeSeriesDataPoint[] = metrics.map((m) => ({
        timestamp: m.timestamp,
        value: m.metric_value,
      }));

      setChartData(dataPoints);

      // Fetch comparison data for all metric types
      const comparisonResults = await Promise.all([
        getMetrics('CPU', undefined, start.toISOString(), end.toISOString(), 'avg', 1, agentId),
        getMetrics('MEMORY', undefined, start.toISOString(), end.toISOString(), 'avg', 1, agentId),
        getMetrics('DISK', undefined, start.toISOString(), end.toISOString(), 'avg', 1, agentId),
        getMetrics('NETWORK', undefined, start.toISOString(), end.toISOString(), 'avg', 1, agentId),
        getMetrics('RESPONSE_TIME', undefined, start.toISOString(), end.toISOString(), 'avg', 1, agentId),
        getMetrics('THROUGHPUT', undefined, start.toISOString(), end.toISOString(), 'avg', 1, agentId),
      ]);

      setComparisonData({
        CPU: comparisonResults[0][0]?.metric_value || 0,
        MEMORY: comparisonResults[1][0]?.metric_value || 0,
        DISK: comparisonResults[2][0]?.metric_value || 0,
        NETWORK: comparisonResults[3][0]?.metric_value || 0,
        RESPONSE_TIME: comparisonResults[4][0]?.metric_value || 0,
        THROUGHPUT: comparisonResults[5][0]?.metric_value || 0,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load chart data');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [metricType, aggregation, timeRange, agentId]);

  const handleZoomIn = () => setZoomLevel((z) => Math.min(z + 0.25, 2));
  const handleZoomOut = () => setZoomLevel((z) => Math.max(z - 0.25, 0.5));
  const handleResetZoom = () => setZoomLevel(1);

  const chartColors: Record<MetricType, string> = {
    CPU: '#3b82f6',
    MEMORY: '#8b5cf6',
    DISK: '#f59e0b',
    NETWORK: '#10b981',
    RESPONSE_TIME: '#ef4444',
    THROUGHPUT: '#06b6d4',
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-500" />
          <p className="text-gray-400">Loading chart data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center text-red-500">
          <p>{error}</p>
          <Button onClick={fetchData} className="mt-4" variant="outline">
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex flex-wrap items-center gap-4">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-gray-400" />
          <Select value={metricType} onValueChange={(v) => setMetricType(v as MetricType)}>
            <SelectTrigger className="w-40 bg-gray-800">
              <SelectValue placeholder="Metric Type" />
            </SelectTrigger>
            <SelectContent className="bg-gray-800">
              <SelectItem value="CPU">CPU</SelectItem>
              <SelectItem value="MEMORY">Memory</SelectItem>
              <SelectItem value="DISK">Disk</SelectItem>
              <SelectItem value="NETWORK">Network</SelectItem>
              <SelectItem value="RESPONSE_TIME">Response Time</SelectItem>
              <SelectItem value="THROUGHPUT">Throughput</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center gap-2">
          <Select value={aggregation} onValueChange={(v) => setAggregation(v as AggregationType)}>
            <SelectTrigger className="w-32 bg-gray-800">
              <SelectValue placeholder="Aggregation" />
            </SelectTrigger>
            <SelectContent className="bg-gray-800">
              <SelectItem value="avg">Average</SelectItem>
              <SelectItem value="sum">Sum</SelectItem>
              <SelectItem value="max">Max</SelectItem>
              <SelectItem value="min">Min</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center gap-2">
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-36 bg-gray-800">
              <SelectValue placeholder="Time Range" />
            </SelectTrigger>
            <SelectContent className="bg-gray-800">
              <SelectItem value="1h">Last Hour</SelectItem>
              <SelectItem value="6h">Last 6 Hours</SelectItem>
              <SelectItem value="24h">Last 24 Hours</SelectItem>
              <SelectItem value="7d">Last 7 Days</SelectItem>
              <SelectItem value="30d">Last 30 Days</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="flex-1" />

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={handleZoomOut}>
            <ZoomOut className="w-4 h-4" />
          </Button>
          <Button variant="outline" size="sm" onClick={handleResetZoom}>
            <Maximize2 className="w-4 h-4" />
          </Button>
          <Button variant="outline" size="sm" onClick={handleZoomIn}>
            <ZoomIn className="w-4 h-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => exportChartAsImage('main-chart', `chart-${metricType.toLowerCase()}`)}
          >
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
          <Button variant="outline" size="sm" onClick={fetchData}>
            <RefreshCw className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Main Line Chart */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <LineChartIcon className="w-4 h-4" />
            {metricType.replace('_', ' ')} Over Time
          </CardTitle>
        </CardHeader>
        <CardContent>
          {chartData.length > 0 ? (
            <div
              id="main-chart"
              className="origin-top-left transition-transform duration-200"
            >
               <SimpleLineChart
                  data={chartData}
                  strokeColor={chartColors[metricType]}
                  height={300 * zoomLevel}
                />
            </div>
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-400">
              <p>No data available for the selected metric</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Comparison Bar Chart */}
      {comparisonData && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-4 h-4" />
              Metric Comparison
            </CardTitle>
          </CardHeader>
          <CardContent>
            <SimpleBarChart
              data={[
                { name: 'CPU', value: comparisonData.CPU, color: chartColors.CPU },
                { name: 'Memory', value: comparisonData.MEMORY, color: chartColors.MEMORY },
                { name: 'Disk', value: comparisonData.DISK, color: chartColors.DISK },
                { name: 'Network', value: comparisonData.NETWORK, color: chartColors.NETWORK },
                { name: 'Response', value: comparisonData.RESPONSE_TIME, color: chartColors.RESPONSE_TIME },
                { name: 'Throughput', value: comparisonData.THROUGHPUT, color: chartColors.THROUGHPUT },
              ]}
              height={250}
            />
          </CardContent>
        </Card>
      )}

      {/* Statistics Cards */}
      {chartData.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <Activity className="w-4 h-4 text-blue-500" />
                <span className="text-sm text-gray-400">Average</span>
              </div>
              <p className="text-2xl font-bold">
                {(chartData.reduce((sum, d) => sum + d.value, 0) / chartData.length).toFixed(2)}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="w-4 h-4 text-green-500" />
                <span className="text-sm text-gray-400">Maximum</span>
              </div>
              <p className="text-2xl font-bold">
                {Math.max(...chartData.map((d) => d.value)).toFixed(2)}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="w-4 h-4 text-red-500 rotate-180" />
                <span className="text-sm text-gray-400">Minimum</span>
              </div>
              <p className="text-2xl font-bold">
                {Math.min(...chartData.map((d) => d.value)).toFixed(2)}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <BarChart3 className="w-4 h-4 text-purple-500" />
                <span className="text-sm text-gray-400">Data Points</span>
              </div>
              <p className="text-2xl font-bold">{chartData.length}</p>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

