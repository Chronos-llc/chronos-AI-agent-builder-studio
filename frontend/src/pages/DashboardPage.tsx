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
    if (percentage >= 90) return 'text-red-600';
    if (percentage >= 75) return 'text-yellow-600';
    return 'text-green-600';
  };

  const getUsageBarColor = () => {
    const percentage = getUsagePercentage();
    if (percentage >= 90) return 'bg-red-500';
    if (percentage >= 75) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome back, {user?.username || 'User'}!
          </h1>
          <p className="text-gray-600 mt-2">
            Manage your AI agents and monitor their performance.
          </p>
        </div>

        {/* Plan Usage Warning */}
        {getUsagePercentage() >= 75 && (
          <div className={`mb-6 p-4 rounded-lg border ${
            getUsagePercentage() >= 90 
              ? 'bg-red-50 border-red-200 text-red-800' 
              : 'bg-yellow-50 border-yellow-200 text-yellow-800'
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
            <p className="mt-1 text-sm">
              Current usage: {stats.thisMonthUsage} / {stats.planLimit} messages this month
            </p>
          </div>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <UsersIcon className="h-8 w-8 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Agents</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.totalAgents}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CheckCircleIcon className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Active Agents</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.activeAgents}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ChartBarIcon className="h-8 w-8 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Messages</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.totalMessages.toLocaleString()}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Cog6ToothIcon className={`h-8 w-8 ${getUsageColor()}`} />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Plan Usage</p>
                <p className={`text-2xl font-semibold ${getUsageColor()}`}>
                  {getUsagePercentage()}%
                </p>
                <p className="text-xs text-gray-500">
                  {stats.thisMonthUsage} / {stats.planLimit} messages
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Usage Progress Bar */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-lg font-medium text-gray-900">Monthly Usage</h3>
            <span className={`text-sm font-medium ${getUsageColor()}`}>
              {getUsagePercentage()}% used
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className={`h-2 rounded-full transition-all duration-300 ${getUsageBarColor()}`}
              style={{ width: `${Math.min(getUsagePercentage(), 100)}%` }}
            ></div>
          </div>
          <p className="text-sm text-gray-600 mt-2">
            {stats.planLimit - stats.thisMonthUsage} messages remaining this month
          </p>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Agents */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900">Recent Agents</h3>
                <Link 
                  to="/agents" 
                  className="text-blue-600 hover:text-blue-500 text-sm font-medium"
                >
                  View all
                </Link>
              </div>
            </div>
            <div className="p-6">
              <Link
                to="/agents/new"
                className="flex items-center justify-center w-full px-4 py-3 border border-dashed border-gray-300 rounded-lg text-gray-500 hover:border-blue-400 hover:text-blue-600 transition-colors"
              >
                <PlusIcon className="h-6 w-6 mr-2" />
                Create New Agent
              </Link>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Recent Activity</h3>
            </div>
            <div className="p-6">
              {recentActivity.length > 0 ? (
                <div className="space-y-4">
                  {recentActivity.slice(0, 5).map((activity) => (
                    <div key={activity.id} className="flex items-start space-x-3">
                      <div className="flex-shrink-0">
                        <div className="h-2 w-2 bg-blue-600 rounded-full mt-2"></div>
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="text-sm text-gray-900">{activity.title}</p>
                        <p className="text-sm text-gray-500">{activity.description}</p>
                        <p className="text-xs text-gray-400 mt-1">
                          {new Date(activity.timestamp).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-4">No recent activity</p>
              )}
            </div>
          </div>
        </div>

        {/* Upgrade Prompt for Free Users */}
        {stats.thisMonthUsage > stats.planLimit * 0.8 && (
          <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium text-blue-900">
                  Need More Usage?
                </h3>
                <p className="text-blue-700 mt-1">
                  Upgrade to Pro for unlimited agents and higher usage limits.
                </p>
              </div>
              <Link
                to="/settings"
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
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