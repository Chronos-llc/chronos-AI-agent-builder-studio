import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ProtectedRoute } from '../components/ProtectedRoute';
import { useAuth } from '../contexts/AuthContext';
import { ProviderLogo } from '../components/brand/ProviderLogo';

interface Integration {
    id: number;
    name: string;
    description: string;
    integration_type: string;
    category: string;
    icon: string;
    documentation_url: string;
    version: string;
    is_public: boolean;
    download_count: number;
    rating: number;
    review_count: number;
    created_at: string;
    updated_at: string;
    author_id: number;
}

interface IntegrationCategory {
    name: string;
    icon: string;
    count: number;
}

const IntegrationsPage: React.FC = () => {
    const { user } = useAuth();
    const navigate = useNavigate();
    const [integrations, setIntegrations] = useState<Integration[]>([]);
    const [categories, setCategories] = useState<IntegrationCategory[]>([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
    const [selectedType, setSelectedType] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);

    const integrationTypes = [
        { name: 'API', icon: '🔌' },
        { name: 'Webhook', icon: '🎣' },
        { name: 'Database', icon: '🗃️' },
        { name: 'File System', icon: '📁' },
        { name: 'MCP Server', icon: '🖥️' },
        { name: 'AI Model', icon: '🤖' },
        { name: 'Communication', icon: '💬' },
        { name: 'WebChat', icon: '🌐' },
    ];

    useEffect(() => {
        fetchIntegrations();
        fetchCategories();
    }, [currentPage, searchQuery, selectedCategory, selectedType]);

    const fetchIntegrations = async () => {
        try {
            setLoading(true);
            setError(null);

            const response = await fetch('/api/v1/integrations/search/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({
                    query: searchQuery,
                    categories: selectedCategory ? [selectedCategory] : null,
                    types: selectedType ? [selectedType.toLowerCase()] : null,
                    page: currentPage,
                    page_size: 12
                })
            });

            if (!response.ok) {
                throw new Error('Failed to fetch integrations');
            }

            const data = await response.json();
            setIntegrations(data);
            setTotalPages(Math.ceil(data.length / 12) || 1);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch integrations');
        } finally {
            setLoading(false);
        }
    };

    const fetchCategories = async () => {
        try {
            // In a real implementation, this would fetch from an API
            const mockCategories = [
                { name: 'Data Sources', icon: '📊', count: 42 },
                { name: 'AI Models', icon: '🤖', count: 28 },
                { name: 'Communication', icon: '💬', count: 15 },
                { name: 'Automation', icon: '⚙️', count: 37 },
                { name: 'Monitoring', icon: '🔍', count: 8 },
                { name: 'Storage', icon: '💾', count: 12 },
                { name: 'Utilities', icon: '🧰', count: 25 },
            ];
            setCategories(mockCategories);
        } catch (err) {
            console.error('Failed to fetch categories:', err);
        }
    };

    const handleInstallIntegration = (integrationId: number) => {
        navigate(`/app/integrations/${integrationId}/install`);
    };

    const handleViewDetails = (integrationId: number) => {
        navigate(`/app/integrations/${integrationId}`);
    };

    const handleCategorySelect = (category: string | null) => {
        setSelectedCategory(category);
        setCurrentPage(1);
    };

    const handleTypeSelect = (type: string | null) => {
        setSelectedType(type);
        setCurrentPage(1);
    };

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        setCurrentPage(1);
    };

    const renderStars = (rating: number) => {
        const fullStars = Math.floor(rating);
        const halfStar = rating % 1 >= 0.5 ? 1 : 0;
        const emptyStars = 5 - fullStars - halfStar;

        return (
            <div className="flex items-center">
                {[...Array(fullStars)].map((_, i) => (
                    <span key={`full-${i}`} className="text-yellow-400">★</span>
                ))}
                {halfStar > 0 && <span className="text-yellow-400">⭐</span>}
                {[...Array(emptyStars)].map((_, i) => (
                    <span key={`empty-${i}`} className="text-gray-300">★</span>
                ))}
                <span className="ml-1 text-sm text-muted-foreground">({rating.toFixed(1)})</span>
            </div>
        );
    };

    return (
        <ProtectedRoute>
            <div className="min-h-screen bg-background p-6">
                <div className="max-w-7xl mx-auto">
                    <h1 className="text-3xl font-bold text-foreground mb-8">Chronos Hub Marketplace</h1>

                    {/* Search and Filters */}
                    <div className="bg-card rounded-lg shadow-sm p-4 mb-6">
                        <div className="flex flex-col lg:flex-row gap-4">
                            <form onSubmit={handleSearch} className="flex-1">
                                <div className="relative">
                                    <input
                                        type="text"
                                        placeholder="Search integrations..."
                                        value={searchQuery}
                                        onChange={(e) => setSearchQuery(e.target.value)}
                                        className="w-full px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    />
                                    <button
                                        type="submit"
                                        className="absolute right-2 top-2 bg-cyan-400 text-white p-1 rounded-md hover:bg-cyan-300"
                                    >
                                        🔍
                                    </button>
                                </div>
                            </form>

                            <div className="flex gap-2 overflow-x-auto">
                                {categories.map((category) => (
                                    <button
                                        key={category.name}
                                        onClick={() => handleCategorySelect(category.name)}
                                        className={`flex items-center gap-1 px-3 py-2 rounded-lg text-sm whitespace-nowrap ${selectedCategory === category.name
                                            ? 'bg-cyan-400 text-white'
                                            : 'bg-gray-200 text-muted-foreground hover:bg-gray-300'
                                            }`}
                                    >
                                        <span>{category.icon}</span>
                                        <span>{category.name}</span>
                                        <span className="bg-background0 text-white text-xs rounded-full px-1 ml-1">{category.count}</span>
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Type Filters */}
                        <div className="mt-4 flex gap-2 overflow-x-auto">
                            {integrationTypes.map((type) => (
                                <button
                                    key={type.name}
                                    onClick={() => handleTypeSelect(type.name)}
                                    className={`flex items-center gap-1 px-3 py-2 rounded-lg text-sm whitespace-nowrap ${selectedType === type.name
                                        ? 'bg-cyan-400 text-white'
                                        : 'bg-gray-200 text-muted-foreground hover:bg-gray-300'
                                        }`}
                                >
                                    <span>{type.icon}</span>
                                    <span>{type.name}</span>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Clear Filters */}
                    {(selectedCategory || selectedType || searchQuery) && (
                        <div className="mb-4">
                            <button
                                onClick={() => {
                                    setSelectedCategory(null);
                                    setSelectedType(null);
                                    setSearchQuery('');
                                    setCurrentPage(1);
                                }}
                                className="text-sm text-muted-foreground hover:text-foreground flex items-center gap-1"
                            >
                                🔄 Clear all filters
                            </button>
                        </div>
                    )}

                    {/* Loading State */}
                    {loading ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                            {[...Array(8)].map((_, i) => (
                                <div key={i} className="bg-card rounded-lg shadow-sm p-4 animate-pulse">
                                    <div className="h-4 bg-gray-200 rounded mb-2"></div>
                                    <div className="h-3 bg-gray-200 rounded mb-2 w-3/4"></div>
                                    <div className="h-6 bg-gray-200 rounded mt-4"></div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <>
                            {/* Error State */}
                            {error && (
                                <div className="bg-rose-500/10 border border-red-200 rounded-lg p-4 mb-6">
                                    <p className="text-rose-400">⚠️ {error}</p>
                                    <button
                                        onClick={fetchIntegrations}
                                        className="mt-2 text-sm text-rose-400 hover:text-red-800"
                                    >
                                        Try again
                                    </button>
                                </div>
                            )}

                            {/* Integrations Grid */}
                            {integrations.length > 0 ? (
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                                    {integrations.map((integration) => (
                                        <div key={integration.id} className="bg-card rounded-lg shadow-sm overflow-hidden hover:shadow-md transition-shadow">
                                            <div className="p-4">
                                                <div className="flex justify-between items-start mb-2">
                                                    <div className="flex items-center gap-2">
                                                        <div className="w-8 h-8 bg-blue-100 rounded-md flex items-center justify-center">
                                                            <ProviderLogo
                                                                name={integration.name}
                                                                url={integration.icon}
                                                                size={24}
                                                                className="border-0 bg-transparent"
                                                            />
                                                        </div>
                                                        <div>
                                                            <h3 className="font-semibold text-foreground">{integration.name}</h3>
                                                            <p className="text-sm text-muted-foreground capitalize">{integration.category.replace('_', ' ')}</p>
                                                        </div>
                                                    </div>
                                                    <span className="text-xs bg-gray-100 text-muted-foreground px-2 py-1 rounded-full">
                                                        v{integration.version}
                                                    </span>
                                                </div>

                                                <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
                                                    {integration.description}
                                                </p>

                                                <div className="flex justify-between items-center mb-3">
                                                    <div className="flex items-center gap-2">
                                                        <span className="text-xs bg-green-100 text-emerald-300 px-2 py-1 rounded-full">
                                                            {integration.integration_type.replace('_', ' ')}
                                                        </span>
                                                        {renderStars(integration.rating)}
                                                    </div>
                                                    <div className="text-xs text-muted-foreground">
                                                        📥 {integration.download_count}
                                                    </div>
                                                </div>

                                                <div className="flex gap-2">
                                                    <button
                                                        onClick={() => handleViewDetails(integration.id)}
                                                        className="flex-1 bg-gray-100 text-muted-foreground py-2 px-3 rounded-md text-sm hover:bg-gray-200 transition-colors"
                                                    >
                                                        View Details
                                                    </button>
                                                    <button
                                                        onClick={() => handleInstallIntegration(integration.id)}
                                                        className="bg-cyan-400 text-white py-2 px-3 rounded-md text-sm hover:bg-cyan-300 transition-colors"
                                                    >
                                                        Install
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="text-center py-12">
                                    <div className="text-6xl text-gray-300 mb-4">🔍</div>
                                    <p className="text-muted-foreground mb-2">No integrations found</p>
                                    <p className="text-sm text-muted-foreground">Try adjusting your search or filters</p>
                                </div>
                            )}
                        </>
                    )}

                    {/* Pagination */}
                    {totalPages > 1 && (
                        <div className="mt-8 flex justify-center items-center gap-2">
                            <button
                                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                                disabled={currentPage === 1}
                                className={`px-3 py-1 rounded-md text-sm ${currentPage === 1
                                    ? 'bg-gray-200 text-muted-foreground/70 cursor-not-allowed'
                                    : 'bg-card text-muted-foreground hover:bg-gray-100'
                                    }`}
                            >
                                ← Previous
                            </button>

                            <span className="text-sm text-muted-foreground">
                                Page {currentPage} of {totalPages}
                            </span>

                            <button
                                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                                disabled={currentPage === totalPages}
                                className={`px-3 py-1 rounded-md text-sm ${currentPage === totalPages
                                    ? 'bg-gray-200 text-muted-foreground/70 cursor-not-allowed'
                                    : 'bg-card text-muted-foreground hover:bg-gray-100'
                                    }`}
                            >
                                Next →
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </ProtectedRoute>
    );
};

export default IntegrationsPage;
