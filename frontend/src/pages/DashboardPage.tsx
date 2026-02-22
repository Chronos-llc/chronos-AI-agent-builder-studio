import React from 'react'
import { useAuth } from '@/contexts/AuthContext'

const DashboardPage: React.FC = () => {
    const { user, logout } = useAuth()

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

                    <div className="mt-8">
                        <div className="card p-6">
                            <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                                <button className="btn btn-primary p-4 text-left">
                                    <div>
                                        <h3 className="font-medium">Create Agent</h3>
                                        <p className="text-sm opacity-75">Build a new AI agent</p>
                                    </div>
                                </button>

                                <button className="btn btn-secondary p-4 text-left">
                                    <div>
                                        <h3 className="font-medium">View Agents</h3>
                                        <p className="text-sm opacity-75">Manage existing agents</p>
                                    </div>
                                </button>

                                <button className="btn btn-outline p-4 text-left">
                                    <div>
                                        <h3 className="font-medium">Integrations</h3>
                                        <p className="text-sm opacity-75">Connect external services</p>
                                    </div>
                                </button>

                                <button className="btn btn-outline p-4 text-left">
                                    <div>
                                        <h3 className="font-medium">Settings</h3>
                                        <p className="text-sm opacity-75">Configure preferences</p>
                                    </div>
                                </button>
                            </div>
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
