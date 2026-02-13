import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Play, 
  Pause, 
  Settings, 
  Trash2, 
  Search, 
  Filter,
  MoreVertical,
  Clock,
  MessageSquare,
  Activity
} from 'lucide-react';
import { PlatformSwitcher } from '../components/studio/PlatformSwitcher';
import { getAgents } from '../services/agentService';
import type { Agent } from '../types/marketplace';

const AgentsPage: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [agentTypeFilter, setAgentTypeFilter] = useState<'text' | 'voice'>('text');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load user's agents
    const loadAgents = async () => {
      try {
        const fetchedAgents = await getAgents(0, 100, undefined, agentTypeFilter);
        setAgents(fetchedAgents);
      } catch (error) {
        console.error('Error loading agents:', error);
        // Mock data if API fails
        const mockAgents: Agent[] = [
          {
            id: 1,
            name: 'DataBot',
            description: 'AI agent specialized in data analysis and reporting',
            status: 'active',
            agent_type: agentTypeFilter,
            usage_count: 1247,
            success_rate: 98.5,
            avg_response_time: 0.8,
            owner_id: 1,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            version: '1.0.0',
            icon: '📊',
            color: '#3B82F6',
            preview_image: 'https://example.com/data-bot-preview.png'
          },
          {
            id: 2,
            name: 'WebHelper',
            description: 'Automates web scraping and content extraction',
            status: 'active',
            agent_type: agentTypeFilter,
            usage_count: 892,
            success_rate: 95.2,
            avg_response_time: 1.2,
            owner_id: 1,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            version: '1.1.0',
            icon: '🌐',
            color: '#10B981',
            preview_image: 'https://example.com/web-helper-preview.png'
          },
          {
            id: 3,
            name: 'ChatBot',
            description: 'Conversational AI for customer support',
            status: 'paused',
            agent_type: agentTypeFilter,
            usage_count: 2341,
            success_rate: 99.1,
            avg_response_time: 0.5,
            owner_id: 1,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            version: '2.0.0',
            icon: '💬',
            color: '#F59E0B',
            preview_image: 'https://example.com/chat-bot-preview.png'
          }
        ];
        setAgents(mockAgents);
      } finally {
        setLoading(false);
      }
    };

    loadAgents();
  }, [agentTypeFilter]);

  const filteredAgents = agents.filter(agent => {
    const matchesSearch = agent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         agent.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         agent.agent_type.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || agent.status === statusFilter;
    const matchesType = agent.agent_type === agentTypeFilter;
    return matchesSearch && matchesStatus && matchesType;
  });

  const handleStatusToggle = (agentId: number, currentStatus: string) => {
    const newStatus = currentStatus === 'active' ? 'paused' : 'active';
    setAgents(prev => prev.map(agent => 
      agent.id === agentId ? { ...agent, status: newStatus as 'active' | 'paused' } : agent
    ));
  };

  const handleDeleteAgent = (agentId: number) => {
    if (confirm('Are you sure you want to delete this agent? This action cannot be undone.')) {
      setAgents(prev => prev.filter(agent => agent.id !== agentId));
    }
  };

  const getStatusBadge = (status: string) => {
    const baseClasses = "px-2 py-1 rounded-full text-xs font-medium";
    switch (status) {
      case 'active':
        return `${baseClasses} bg-emerald-500/15 text-emerald-200`;
      case 'paused':
        return `${baseClasses} bg-amber-500/15 text-amber-200`;
      case 'error':
        return `${baseClasses} bg-rose-500/15 text-rose-200`;
      default:
        return `${baseClasses} bg-muted text-muted-foreground`;
    }
  };

  const getPerformanceColor = (performance: number) => {
    if (performance >= 95) return 'text-emerald-400';
    if (performance >= 90) return 'text-amber-400';
    return 'text-rose-400';
  };

  if (loading) {
    return (
      <div className="page-container">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">My Agents</h1>
          <Link to="/app/agents/new" className="btn btn-primary">
            Create New Agent
          </Link>
        </div>
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-300"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap justify-between gap-4 items-center">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-white/50">Workspace</p>
          <h1 className="mt-2 text-2xl font-bold text-white">My Agents</h1>
          <p className="text-white/65 mt-1">Manage your AI agent workspace</p>
        </div>
        <div className="flex items-center gap-4">
          <PlatformSwitcher 
            value={agentTypeFilter} 
            onChange={setAgentTypeFilter} 
            className="hidden md:block"
          />
          <Link to="/app/agents/new" className="btn btn-primary">
            Create New Agent
          </Link>
        </div>
      </div>

      {/* Mobile Platform Switcher */}
      <div className="md:hidden mb-6">
        <PlatformSwitcher 
          value={agentTypeFilter} 
          onChange={setAgentTypeFilter} 
          className="w-full"
        />
      </div>

      {/* Search and Filters */}
      <div className="chronos-surface p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground/70 w-4 h-4" />
            <input
              type="text"
              placeholder="Search agents by name, description, or type..."
              className="input pl-10 w-full bg-black/25"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground/70 w-4 h-4" />
            <select
              className="input pl-10 pr-8 appearance-none bg-black/25 min-w-[150px]"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              aria-label="Filter by status"
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="paused">Paused</option>
              <option value="error">Error</option>
            </select>
          </div>
        </div>
      </div>

      {/* Agents Grid */}
      {filteredAgents.length === 0 ? (
        <div className="chronos-surface p-8 text-center">
          <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
            <Activity className="w-8 h-8 text-muted-foreground/70" />
          </div>
          <h2 className="text-xl font-semibold mb-2">
            {agents.length === 0 ? 'No agents yet' : 'No agents match your search'}
          </h2>
          <p className="text-muted-foreground mb-4">
            {agents.length === 0 
              ? 'Get started by creating your first AI agent'
              : 'Try adjusting your search or filter criteria'
            }
          </p>
          {agents.length === 0 && (
            <Link to="/app/agents/new" className="btn btn-primary">
              Create Agent
            </Link>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
           {filteredAgents.map((agent) => (
            <div key={agent.id} className="chronos-surface p-5 hover:shadow-glow transition-shadow">
              {/* Agent Header */}
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold mb-1">{agent.name}</h3>
                  <span className={`text-sm px-2 py-1 rounded ${
                    agent.agent_type === 'voice' 
                      ? 'text-violet-200 bg-violet-500/15' 
                      : 'text-cyan-200 bg-cyan-500/15'
                  }`}>
                    {agent.agent_type === 'voice' ? 'Voice Agent' : 'Text Agent'}
                  </span>
                </div>
                <div className="relative">
                  <button 
                    type="button"
                    className="p-1 hover:bg-muted rounded"
                    title="More options"
                    aria-label="More options"
                  >
                    <MoreVertical className="w-4 h-4 text-muted-foreground" />
                  </button>
                </div>
              </div>

              {/* Agent Description */}
              <p className="text-muted-foreground text-sm mb-4 line-clamp-2">
                {agent.description || 'No description provided'}
              </p>

              {/* Status and Performance */}
              <div className="flex justify-between items-center mb-4">
                <span className={getStatusBadge(agent.status)}>
                  {agent.status.charAt(0).toUpperCase() + agent.status.slice(1)}
                </span>
                <span className={`text-sm font-medium ${getPerformanceColor(agent.success_rate)}`}>
                  {agent.success_rate}% perf
                </span>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                <div className="flex items-center text-muted-foreground">
                  <MessageSquare className="w-4 h-4 mr-2" />
                  <span>{agent.usage_count.toLocaleString()} interactions</span>
                </div>
                <div className="flex items-center text-muted-foreground">
                  <Clock className="w-4 h-4 mr-2" />
                  <span>{new Date(agent.updated_at).toLocaleDateString()}</span>
                </div>
              </div>

              {/* Actions */}
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() => handleStatusToggle(agent.id, agent.status)}
                  className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded text-sm font-medium transition-colors ${
                    agent.status === 'active'
                      ? 'bg-amber-500/15 text-amber-200 hover:bg-amber-500/25'
                      : 'bg-emerald-500/15 text-emerald-200 hover:bg-emerald-500/25'
                  }`}
                >
                  {agent.status === 'active' ? (
                    <>
                      <Pause className="w-4 h-4" />
                      Pause
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4" />
                      Start
                    </>
                  )}
                </button>
                <Link
                  to={`/app/agents/${agent.id}/suite`}
                  className="flex items-center justify-center px-3 py-2 bg-cyan-500/15 text-cyan-200 rounded hover:bg-cyan-500/25 transition-colors text-sm font-medium"
                  title="Open in Suite"
                  aria-label="Open in suite"
                >
                  Suite
                </Link>
                <Link
                  to={`/app/agents/${agent.id}/edit`}
                  className="flex items-center justify-center px-3 py-2 bg-black/25 text-muted-foreground rounded hover:bg-muted hover:text-foreground transition-colors"
                  title="Settings"
                  aria-label="Settings"
                >
                  <Settings className="w-4 h-4" />
                </Link>
                <button
                  type="button"
                  onClick={() => handleDeleteAgent(agent.id)}
                  className="flex items-center justify-center px-3 py-2 bg-rose-500/15 text-rose-200 rounded hover:bg-rose-500/25 transition-colors"
                  title="Delete agent"
                  aria-label="Delete agent"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Quick Stats Footer */}
      {filteredAgents.length > 0 && (
        <div className="mt-8 grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="chronos-surface p-4 text-center">
            <div className="text-2xl font-bold text-cyan-300">{filteredAgents.length}</div>
            <div className="text-sm text-muted-foreground">Total {agentTypeFilter.charAt(0).toUpperCase() + agentTypeFilter.slice(1)} Agents</div>
          </div>
          <div className="chronos-surface p-4 text-center">
            <div className="text-2xl font-bold text-emerald-400">
              {filteredAgents.filter(a => a.status === 'active').length}
            </div>
            <div className="text-sm text-muted-foreground">Active</div>
          </div>
          <div className="chronos-surface p-4 text-center">
            <div className="text-2xl font-bold text-amber-400">
              {filteredAgents.filter(a => a.status === 'paused').length}
            </div>
            <div className="text-sm text-muted-foreground">Paused</div>
          </div>
          <div className="chronos-surface p-4 text-center">
            <div className="text-2xl font-bold text-sky-400">
              {filteredAgents.reduce((sum, a) => sum + a.usage_count, 0).toLocaleString()}
            </div>
            <div className="text-sm text-muted-foreground">Total Interactions</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentsPage;
