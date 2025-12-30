import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
    GitBranch,
    GitCommit,
    GitPullRequest,
    Clock,
    Download,
    Upload,
    RotateCcw,
    Eye,
    Plus,
    Tag,
    FileText,
    Users,
    CheckCircle,
    AlertCircle,
    Loader2
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface AgentVersion {
    id: number;
    version_number: string;
    changelog: string;
    is_current: boolean;
    config_snapshot: any;
    agent_id: number;
    created_at: string;
    created_by?: {
        id: number;
        name: string;
        email: string;
    };
}

interface VersionDiff {
    field: string;
    old_value: any;
    new_value: any;
    change_type: 'added' | 'removed' | 'modified';
}

const VersionControlPanel: React.FC<{ agentId: number }> = ({ agentId }) => {
    const [activeTab, setActiveTab] = useState<'history' | 'compare' | 'rollback'>('history');
    const [selectedVersions, setSelectedVersions] = useState<number[]>([]);
    const [showVersionModal, setShowVersionModal] = useState(false);
    const [newVersion, setNewVersion] = useState({
        version_number: '',
        changelog: '',
        is_current: false
    });

    const queryClient = useQueryClient();

    // Fetch version history
    const { data: versions, isLoading } = useQuery({
        queryKey: ['agent-versions', agentId],
        queryFn: async () => {
            const response = await fetch(`/api/agents/${agentId}/versions`);
            if (!response.ok) throw new Error('Failed to fetch versions');
            return response.json();
        }
    });

    // Create new version
    const createVersionMutation = useMutation({
        mutationFn: async (versionData: any) => {
            const response = await fetch(`/api/agents/${agentId}/versions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(versionData)
            });
            if (!response.ok) throw new Error('Failed to create version');
            return response.json();
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['agent-versions', agentId] });
            setShowVersionModal(false);
            setNewVersion({ version_number: '', changelog: '', is_current: false });
        }
    });

    // Rollback to version
    const rollbackMutation = useMutation({
        mutationFn: async (versionId: number) => {
            const response = await fetch(`/api/agents/${agentId}/versions/${versionId}/rollback`, {
                method: 'POST'
            });
            if (!response.ok) throw new Error('Failed to rollback version');
            return response.json();
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['agent-versions', agentId] });
            queryClient.invalidateQueries({ queryKey: ['agent', agentId] });
        }
    });

    // Compare versions
    const [compareResults, setCompareResults] = useState<VersionDiff[]>([]);
    const compareVersions = async () => {
        if (selectedVersions.length !== 2) return;

        try {
            const response = await fetch(`/api/agents/${agentId}/versions/compare`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    version1_id: selectedVersions[0],
                    version2_id: selectedVersions[1]
                })
            });
            if (response.ok) {
                const diff = await response.json();
                setCompareResults(diff);
            }
        } catch (error) {
            console.error('Comparison failed:', error);
        }
    };

    const getVersionStatus = (version: AgentVersion) => {
        if (version.is_current) return 'current';
        return 'historical';
    };

    const getVersionIcon = (version: AgentVersion) => {
        if (version.is_current) return <CheckCircle className="w-4 h-4 text-green-500" />;
        return <GitCommit className="w-4 h-4 text-blue-500" />;
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <Loader2 className="w-6 h-6 animate-spin" />
                <span className="ml-2">Loading version history...</span>
            </div>
        );
    }

    return (
        <div className="h-full flex flex-col">
            {/* Header */}
            <div className="border-b border-gray-200 pb-4 mb-6">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                        <GitBranch className="w-6 h-6 text-blue-600" />
                        <h2 className="text-xl font-semibold text-gray-900">Version Control</h2>
                    </div>
                    <button
                        onClick={() => setShowVersionModal(true)}
                        className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                        <Plus className="w-4 h-4" />
                        <span>New Version</span>
                    </button>
                </div>

                {/* Tabs */}
                <div className="flex space-x-1 mt-4">
                    {[
                        { id: 'history', label: 'History', icon: Clock },
                        { id: 'compare', label: 'Compare', icon: GitPullRequest },
                        { id: 'rollback', label: 'Rollback', icon: RotateCcw }
                    ].map(({ id, label, icon: Icon }) => (
                        <button
                            key={id}
                            onClick={() => setActiveTab(id as any)}
                            className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${activeTab === id
                                    ? 'bg-blue-100 text-blue-700'
                                    : 'text-gray-600 hover:bg-gray-100'
                                }`}
                        >
                            <Icon className="w-4 h-4" />
                            <span>{label}</span>
                        </button>
                    ))}
                </div>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-auto">
                {activeTab === 'history' && (
                    <div className="space-y-4">
                        {versions?.map((version: AgentVersion) => (
                            <div
                                key={version.id}
                                className={`border rounded-lg p-4 transition-colors ${version.is_current ? 'border-green-200 bg-green-50' : 'border-gray-200'
                                    }`}
                            >
                                <div className="flex items-start justify-between">
                                    <div className="flex items-start space-x-3">
                                        {getVersionIcon(version)}
                                        <div className="flex-1">
                                            <div className="flex items-center space-x-2">
                                                <h3 className="font-medium text-gray-900">
                                                    Version {version.version_number}
                                                </h3>
                                                {version.is_current && (
                                                    <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                                                        Current
                                                    </span>
                                                )}
                                            </div>
                                            {version.changelog && (
                                                <p className="text-sm text-gray-600 mt-1">{version.changelog}</p>
                                            )}
                                            <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                                                <span className="flex items-center space-x-1">
                                                    <Clock className="w-3 h-3" />
                                                    <span>
                                                        {formatDistanceToNow(new Date(version.created_at), { addSuffix: true })}
                                                    </span>
                                                </span>
                                                {version.created_by && (
                                                    <span className="flex items-center space-x-1">
                                                        <Users className="w-3 h-3" />
                                                        <span>{version.created_by.name}</span>
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <button className="p-2 text-gray-400 hover:text-blue-600 transition-colors" title="View version details">
                                            <Eye className="w-4 h-4" />
                                        </button>
                                        {!version.is_current && (
                                            <button
                                                onClick={() => rollbackMutation.mutate(version.id)}
                                                disabled={rollbackMutation.isPending}
                                                className="p-2 text-gray-400 hover:text-orange-600 transition-colors"
                                                title="Rollback to this version"
                                            >
                                                <RotateCcw className="w-4 h-4" />
                                            </button>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {activeTab === 'compare' && (
                    <div className="space-y-4">
                        <div className="border border-gray-200 rounded-lg p-4">
                            <h3 className="font-medium mb-4">Select Versions to Compare</h3>
                            <div className="grid grid-cols-2 gap-4 mb-4">
                                {versions?.map((version: AgentVersion) => (
                                    <div
                                        key={version.id}
                                        className={`border rounded-lg p-3 cursor-pointer transition-colors ${selectedVersions.includes(version.id)
                                                ? 'border-blue-500 bg-blue-50'
                                                : 'border-gray-200 hover:border-gray-300'
                                            }`}
                                        onClick={() => {
                                            setSelectedVersions(prev => {
                                                if (prev.includes(version.id)) {
                                                    return prev.filter(id => id !== version.id);
                                                } else if (prev.length < 2) {
                                                    return [...prev, version.id];
                                                } else {
                                                    return [prev[1], version.id];
                                                }
                                            });
                                        }}
                                    >
                                        <div className="flex items-center space-x-2">
                                            {getVersionIcon(version)}
                                            <div>
                                                <div className="font-medium">Version {version.version_number}</div>
                                                <div className="text-sm text-gray-500">
                                                    {formatDistanceToNow(new Date(version.created_at), { addSuffix: true })}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                            {selectedVersions.length === 2 && (
                                <button
                                    onClick={compareVersions}
                                    className="w-full py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                                >
                                    Compare Versions
                                </button>
                            )}
                        </div>

                        {compareResults.length > 0 && (
                            <div className="border border-gray-200 rounded-lg p-4">
                                <h3 className="font-medium mb-4">Differences</h3>
                                <div className="space-y-3">
                                    {compareResults.map((diff, index) => (
                                        <div key={index} className="border-l-4 pl-4">
                                            <div className="font-medium text-sm">{diff.field}</div>
                                            <div className="text-sm">
                                                <span className="text-red-600 line-through">{diff.old_value}</span>
                                                <span className="mx-2">→</span>
                                                <span className="text-green-600">{diff.new_value}</span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {activeTab === 'rollback' && (
                    <div className="space-y-4">
                        <div className="border border-orange-200 bg-orange-50 rounded-lg p-4">
                            <div className="flex items-start space-x-3">
                                <AlertCircle className="w-5 h-5 text-orange-600 mt-0.5" />
                                <div>
                                    <h3 className="font-medium text-orange-900">Rollback Warning</h3>
                                    <p className="text-sm text-orange-700 mt-1">
                                        Rolling back will replace the current configuration with the selected version.
                                        This action cannot be undone. Consider creating a new version first.
                                    </p>
                                </div>
                            </div>
                        </div>

                        {versions?.filter((v: AgentVersion) => !v.is_current).map((version: AgentVersion) => (
                            <div key={version.id} className="border border-gray-200 rounded-lg p-4">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <h3 className="font-medium">Version {version.version_number}</h3>
                                        {version.changelog && (
                                            <p className="text-sm text-gray-600 mt-1">{version.changelog}</p>
                                        )}
                                        <div className="text-xs text-gray-500 mt-2">
                                            Created {formatDistanceToNow(new Date(version.created_at), { addSuffix: true })}
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => rollbackMutation.mutate(version.id)}
                                        disabled={rollbackMutation.isPending}
                                        className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors disabled:opacity-50"
                                    >
                                        {rollbackMutation.isPending ? 'Rolling Back...' : 'Rollback'}
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Create Version Modal */}
            {showVersionModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 w-full max-w-md">
                        <h3 className="text-lg font-medium mb-4">Create New Version</h3>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Version Number
                                </label>
                                <input
                                    type="text"
                                    value={newVersion.version_number}
                                    onChange={(e) => setNewVersion(prev => ({ ...prev, version_number: e.target.value }))}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                    placeholder="e.g., 1.0.0"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Changelog
                                </label>
                                <textarea
                                    value={newVersion.changelog}
                                    onChange={(e) => setNewVersion(prev => ({ ...prev, changelog: e.target.value }))}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                    rows={3}
                                    placeholder="Describe what changed in this version..."
                                />
                            </div>
                            <div className="flex items-center">
                                <input
                                    type="checkbox"
                                    id="is_current"
                                    checked={newVersion.is_current}
                                    onChange={(e) => setNewVersion(prev => ({ ...prev, is_current: e.target.checked }))}
                                    className="mr-2"
                                />
                                <label htmlFor="is_current" className="text-sm text-gray-700">
                                    Set as current version
                                </label>
                            </div>
                        </div>
                        <div className="flex space-x-3 mt-6">
                            <button
                                onClick={() => setShowVersionModal(false)}
                                className="flex-1 px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={() => createVersionMutation.mutate(newVersion)}
                                disabled={createVersionMutation.isPending || !newVersion.version_number}
                                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                            >
                                {createVersionMutation.isPending ? 'Creating...' : 'Create Version'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default VersionControlPanel;