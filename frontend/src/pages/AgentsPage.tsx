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

  const handleStatusToggle = (agentId: string, currentStatus: string) => {
    const newStatus = currentStatus === 'active' ? 'paused' : 'active';
    setAgents(prev => prev.map(agent => 
      agent.id === agentId ? { ...agent, status: newStatus as 'active' | 'paused' } : agent
    ));
  };

  const handleDeleteAgent = (agentId: string) => {
    if (confirm('Are you sure you want to delete this agent? This action cannot be undone.')) {
      setAgents(prev => prev.filter(agent => agent.id !== agentId));
    }
  };

  const getStatusBadge = (status: string) => {
    const baseClasses = "px-2 py-1 rounded-full text-xs font-medium";
    switch (status) {
      case 'active':
        return `${baseClasses} bg-green-100 text-green-800`;
      case 'paused':
        return `${baseClasses} bg-yellow-100 text-yellow-800`;
      case 'error':
        return `${baseClasses} bg-red-100 text-red-800`;
      default:
        return `${baseClasses} bg-gray-100 text-gray-800`;
    }
  };

  const getPerformanceColor = (performance: number) => {
    if (performance >= 95) return 'text-green-600';
    if (performance >= 90) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className="page-container">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">My Agents</h1>
          <Link to="/agents/new" className="btn btn-primary">
            Create New Agent
          </Link>
        </div>
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold">My Agents</h1>
          <p className="text-gray-600 mt-1">Manage your AI agent workspace</p>
        </div>
        <div className="flex items-center gap-4">
          <PlatformSwitcher 
            value={agentTypeFilter} 
            onChange={setAgentTypeFilter} 
            className="hidden md:block"
          />
          <Link to="/agents/new" className="btn btn-primary">
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
      <div className="card p-4 mb-6">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search agents by name, description, or type..."
              className="input pl-10 w-full"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <select
              className="input pl-10 pr-8 appearance-none bg-white min-w-[150px]"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
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
        <div className="card p-8 text-center">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Activity className="w-8 h-8 text-gray-400" />
          </div>
          <h2 className="text-xl font-semibold mb-2">
            {agents.length === 0 ? 'No agents yet' : 'No agents match your search'}
          </h2>
          <p className="text-gray-600 mb-4">
            {agents.length === 0 
              ? 'Get started by creating your first AI agent'
              : 'Try adjusting your search or filter criteria'
            }
          </p>
          {agents.length === 0 && (
            <Link to="/agents/new" className="btn btn-primary">
              Create Agent
            </Link>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
           {filteredAgents.map((agent) => (
            <div key={agent.id} className="card hover:shadow-lg transition-shadow">
              {/* Agent Header */}
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold mb-1">{agent.name}</h3>
                  <span className={`text-sm px-2 py-1 rounded ${
                    agent.agent_type === 'voice' 
                      ? 'text-purple-600 bg-purple-50' 
                      : 'text-blue-600 bg-blue-50'
                  }`}>
                    {agent.agent_type === 'voice' ? 'Voice Agent' : 'Text Agent'}
                  </span>
                </div>
                <div className="relative">
                  <button className="p-1 hover:bg-gray-100 rounded">
                    <MoreVertical className="w-4 h-4 text-gray-600" />
                  </button>
                </div>
              </div>

              {/* Agent Description */}
              <p className="text-gray-600 text-sm mb-4 line-clamp-2">
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
                <div className="flex items-center text-gray-600">
                  <MessageSquare className="w-4 h-4 mr-2" />
                  <span>{agent.usage_count.toLocaleString()} interactions</span>
                </div>
                <div className="flex items-center text-gray-600">
                  <Clock className="w-4 h-4 mr-2" />
                  <span>{new Date(agent.updated_at).toLocaleDateString()}</span>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-2">
                <button
                  onClick={() => handleStatusToggle(agent.id, agent.status)}
                  className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded text-sm font-medium transition-colors ${
                    agent.status === 'active'
                      ? 'bg-yellow-50 text-yellow-700 hover:bg-yellow-100'
                      : 'bg-green-50 text-green-700 hover:bg-green-100'
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
                  to={`/agents/${agent.id}/edit`}
                  className="flex items-center justify-center px-3 py-2 bg-gray-50 text-gray-700 rounded hover:bg-gray-100 transition-colors"
                >
                  <Settings className="w-4 h-4" />
                </Link>
                <button
                  onClick={() => handleDeleteAgent(agent.id)}
                  className="flex items-center justify-center px-3 py-2 bg-red-50 text-red-700 rounded hover:bg-red-100 transition-colors"
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
          <div className="card p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">{filteredAgents.length}</div>
            <div className="text-sm text-gray-600">Total {agentTypeFilter.charAt(0).toUpperCase() + agentTypeFilter.slice(1)} Agents</div>
          </div>
          <div className="card p-4 text-center">
            <div className="text-2xl font-bold text-green-600">
              {filteredAgents.filter(a => a.status === 'active').length}
            </div>
            <div className="text-sm text-gray-600">Active</div>
          </div>
          <div className="card p-4 text-center">
            <div className="text-2xl font-bold text-yellow-600">
              {filteredAgents.filter(a => a.status === 'paused').length}
            </div>
            <div className="text-sm text-gray-600">Paused</div>
          </div>
          <div className="card p-4 text-center">
            <div className="text-2xl font-bold text-purple-600">
              {filteredAgents.reduce((sum, a) => sum + a.usage_count, 0).toLocaleString()}
            </div>
            <div className="text-sm text-gray-600">Total Interactions</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentsPage;