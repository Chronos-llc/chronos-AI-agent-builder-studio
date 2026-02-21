import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  PlusIcon, 
  UsersIcon, 
  ChartBarIcon, 
  Cog6ToothIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import { PlatformLoadingScreen } from '../components/loading/PlatformLoadingScreen';

interface DashboardStats {
  totalAgents: number;
  activeAgents: number;
  totalMessages: number;
  thisMonthUsage: number;
  planLimit: number;
}

interface RecentActivity {
  id: string;
  type: 'agent_created' | 'agent_updated' | 'message_sent' | 'integration_connected';
  title: string;
  description: string;
  timestamp: string;
  agentName?: string;
}

const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats>({
    totalAgents: 0,
    activeAgents: 0,
    totalMessages: 0,
    thisMonthUsage: 0,
    planLimit: 1000
  });
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch dashboard statistics
      const statsResponse = await fetch('/api/dashboard/stats', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStats(statsData);
      }

      // Fetch recent activity
      const activityResponse = await fetch('/api/dashboard/activity', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (activityResponse.ok) {
        const activityData = await activityResponse.json();
        setRecentActivity(activityData);
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getUsagePercentage = () => {
    return Math.round((stats.thisMonthUsage / stats.planLimit) * 100);
  };

  const getUsageColor = () => {
    const percentage = getUsagePercentage();
    if (percentage >= 90) return 'text-rose-400';
    if (percentage >= 75) return 'text-amber-400';
    return 'text-emerald-400';
  };

  const getUsageBarColor = () => {
    const percentage = getUsagePercentage();
    if (percentage >= 90) return 'bg-rose-500';
    if (percentage >= 75) return 'bg-amber-400';
    return 'bg-emerald-500';
  };

  if (loading) {
    return <PlatformLoadingScreen mode="overlay" />;
  }

  return (
    <div className="space-y-6">
      <div>
        {/* Header */}
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-white/50">Overview</p>
          <h1 className="mt-2 text-3xl font-bold text-white">
            Welcome back, {user?.username || 'User'}!
          </h1>
          <p className="mt-2 text-white/65">
            Manage your AI agents and monitor their performance.
          </p>
        </div>

        {/* Plan Usage Warning */}
        {getUsagePercentage() >= 75 && (
          <div className={`mb-6 p-4 rounded-lg border ${
            getUsagePercentage() >= 90 
              ? 'bg-rose-500/10 border-rose-500/30 text-rose-100' 
              : 'bg-amber-500/10 border-amber-500/30 text-amber-100'
          }`}>
            <div className="flex items-center">
              <ExclamationTriangleIcon className="h-5 w-5 mr-2" />
              <span className="font-medium">
                {getUsagePercentage() >= 90 
                  ? 'Critical: You are approaching your plan limits!' 
                  : 'Warning: You are using most of your plan allocation.'
                }
              </span>
            </div>
            <p className="mt-1 text-sm text-white/70">
              Current usage: {stats.thisMonthUsage} / {stats.planLimit} messages this month
            </p>
          </div>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="chronos-surface p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <UsersIcon className="h-8 w-8 text-cyan-300" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Total Agents</p>
                <p className="text-2xl font-semibold text-foreground">{stats.totalAgents}</p>
              </div>
            </div>
          </div>

          <div className="chronos-surface p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CheckCircleIcon className="h-8 w-8 text-emerald-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Active Agents</p>
                <p className="text-2xl font-semibold text-foreground">{stats.activeAgents}</p>
              </div>
            </div>
          </div>

          <div className="chronos-surface p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ChartBarIcon className="h-8 w-8 text-sky-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Total Messages</p>
                <p className="text-2xl font-semibold text-foreground">{stats.totalMessages.toLocaleString()}</p>
              </div>
            </div>
          </div>

          <div className="chronos-surface p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Cog6ToothIcon className={`h-8 w-8 ${getUsageColor()}`} />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Plan Usage</p>
                <p className={`text-2xl font-semibold ${getUsageColor()}`}>
                  {getUsagePercentage()}%
                </p>
                <p className="text-xs text-muted-foreground">
                  {stats.thisMonthUsage} / {stats.planLimit} messages
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Usage Progress Bar */}
        <div className="chronos-surface p-6 mb-8">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-lg font-medium text-foreground">Monthly Usage</h3>
            <span className={`text-sm font-medium ${getUsageColor()}`}>
              {getUsagePercentage()}% used
            </span>
          </div>
          <div className="w-full bg-muted rounded-full h-2">
            <div 
              className={`h-2 rounded-full transition-all duration-300 ${getUsageBarColor()}`}
              style={{ width: `${Math.min(getUsagePercentage(), 100)}%` }}
            ></div>
          </div>
          <p className="text-sm text-muted-foreground mt-2">
            {stats.planLimit - stats.thisMonthUsage} messages remaining this month
          </p>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Agents */}
          <div className="chronos-surface">
            <div className="p-6 border-b border-border">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-foreground">Recent Agents</h3>
                <Link 
                  to="/app/agents" 
                  className="text-cyan-300 hover:text-cyan-200 text-sm font-medium"
                >
                  View all
                </Link>
              </div>
            </div>
            <div className="p-6">
              <Link
                to="/app/agents/new"
                className="flex items-center justify-center w-full px-4 py-3 border border-dashed border-border rounded-lg text-muted-foreground hover:border-cyan-300 hover:text-cyan-300 transition-colors"
              >
                <PlusIcon className="h-6 w-6 mr-2" />
                Create New Agent
              </Link>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="chronos-surface">
            <div className="p-6 border-b border-border">
              <h3 className="text-lg font-medium text-foreground">Recent Activity</h3>
            </div>
            <div className="p-6">
              {recentActivity.length > 0 ? (
                <div className="space-y-4">
                  {recentActivity.slice(0, 5).map((activity) => (
                    <div key={activity.id} className="flex items-start space-x-3">
                      <div className="flex-shrink-0">
                        <div className="h-2 w-2 bg-cyan-400 rounded-full mt-2"></div>
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="text-sm text-foreground">{activity.title}</p>
                        <p className="text-sm text-muted-foreground">{activity.description}</p>
                        <p className="text-xs text-muted-foreground/70 mt-1">
                          {new Date(activity.timestamp).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground text-center py-4">No recent activity</p>
              )}
            </div>
          </div>
        </div>

        {/* Upgrade Prompt for Free Users */}
        {stats.thisMonthUsage > stats.planLimit * 0.8 && (
          <div className="mt-8 bg-cyan-500/10 border border-cyan-500/30 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium text-cyan-200">
                  Need More Usage?
                </h3>
                <p className="text-cyan-100/70 mt-1">
                  Upgrade to Pro for unlimited agents and higher usage limits.
                </p>
              </div>
              <Link
                to="/app/settings"
                className="bg-cyan-400 text-[#0B1016] px-4 py-2 rounded-lg hover:bg-cyan-300 transition-colors"
              >
                Upgrade Now
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;
