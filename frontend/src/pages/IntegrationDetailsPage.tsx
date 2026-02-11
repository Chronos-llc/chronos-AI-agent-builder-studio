import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ProtectedRoute } from '../components/ProtectedRoute';
import { useAuth } from '../contexts/AuthContext';

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
    config_schema: any;
    credentials_schema: any;
    supported_features: string[];
}

interface Review {
    id: number;
    user_id: number;
    rating: number;
    comment: string;
    created_at: string;
    updated_at: string;
    username: string;
}

const IntegrationDetailsPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const { user } = useAuth();
    const navigate = useNavigate();
    const [integration, setIntegration] = useState<Integration | null>(null);
    const [reviews, setReviews] = useState<Review[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [activeTab, setActiveTab] = useState<'details' | 'reviews' | 'setup'>('details');
    const [userReview, setUserReview] = useState({ rating: 5, comment: '' });
    const [hasReviewed, setHasReviewed] = useState(false);

    useEffect(() => {
        if (id) {
            fetchIntegrationDetails(parseInt(id));
            fetchReviews(parseInt(id));
        }
    }, [id]);

    const fetchIntegrationDetails = async (integrationId: number) => {
        try {
            setLoading(true);
            setError(null);

            const response = await fetch(`/api/v1/integrations/${integrationId}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) {
                throw new Error('Failed to fetch integration details');
            }

            const data = await response.json();
            setIntegration(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch integration details');
        } finally {
            setLoading(false);
        }
    };

    const fetchReviews = async (integrationId: number) => {
        try {
            // In a real implementation, this would fetch from an API
            const mockReviews: Review[] = [
                {
                    id: 1,
                    user_id: 1,
                    rating: 5,
                    comment: 'This integration is amazing! Works perfectly with my AI agents.',
                    created_at: '2023-01-15T10:30:00Z',
                    updated_at: '2023-01-15T10:30:00Z',
                    username: 'ai_enthusiast'
                },
                {
                    id: 2,
                    user_id: 2,
                    rating: 4,
                    comment: 'Great integration, but the documentation could be more detailed.',
                    created_at: '2023-02-20T14:15:00Z',
                    updated_at: '2023-02-20T14:15:00Z',
                    username: 'dev_guru'
                },
                {
                    id: 3,
                    user_id: 3,
                    rating: 5,
                    comment: 'Perfect for my use case. Easy to set up and very reliable.',
                    created_at: '2023-03-10T09:45:00Z',
                    updated_at: '2023-03-10T09:45:00Z',
                    username: 'tech_leader'
                }
            ];
            setReviews(mockReviews);

            // Check if current user has already reviewed
            if (user) {
                const userReview = mockReviews.find(r => r.user_id === user.id);
                setHasReviewed(!!userReview);
            }
        } catch (err) {
            console.error('Failed to fetch reviews:', err);
        }
    };

    const handleInstall = () => {
        if (id) {
            navigate(`/app/integrations/${id}/install`);
        }
    };

    const handleSubmitReview = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!user || !id) return;

        try {
            const response = await fetch(`/api/v1/integrations/${id}/reviews/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({
                    rating: userReview.rating,
                    comment: userReview.comment
                })
            });

            if (!response.ok) {
                throw new Error('Failed to submit review');
            }

            // Refresh reviews
            fetchReviews(parseInt(id));
            setHasReviewed(true);
            setUserReview({ rating: 5, comment: '' });
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to submit review');
        }
    };

    const renderStars = (rating: number) => {
        const fullStars = Math.floor(rating);
        const halfStar = rating % 1 >= 0.5 ? 1 : 0;
        const emptyStars = 5 - fullStars - halfStar;

        return (
            <div className="flex items-center">
                {[...Array(fullStars)].map((_, i) => (
                    <span key={`full-${i}`} className="text-yellow-400 text-lg">★</span>
                ))}
                {halfStar > 0 && <span className="text-yellow-400 text-lg">⭐</span>}
                {[...Array(emptyStars)].map((_, i) => (
                    <span key={`empty-${i}`} className="text-gray-300 text-lg">★</span>
                ))}
            </div>
        );
    };

    const renderEditableStars = () => {
        return (
            <div className="flex items-center">
                {[1, 2, 3, 4, 5].map((star) => (
                    <button
                        key={star}
                        onClick={() => setUserReview({ ...userReview, rating: star })}
                        className={`text-2xl ${star <= userReview.rating ? 'text-yellow-400' : 'text-gray-300'}`}
                    >
                        {star <= userReview.rating ? '★' : '☆'}
                    </button>
                ))}
            </div>
        );
    };

    if (loading) {
        return (
            <ProtectedRoute>
                <div className="min-h-screen bg-background p-6">
                    <div className="max-w-4xl mx-auto">
                        <div className="bg-card rounded-lg shadow-sm p-6 animate-pulse">
                            <div className="h-8 bg-gray-200 rounded mb-4 w-1/3"></div>
                            <div className="h-4 bg-gray-200 rounded mb-2 w-full"></div>
                            <div className="h-4 bg-gray-200 rounded mb-4 w-2/3"></div>
                            <div className="h-6 bg-gray-200 rounded mb-6 w-1/4"></div>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="h-4 bg-gray-200 rounded"></div>
                                <div className="h-4 bg-gray-200 rounded"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </ProtectedRoute>
        );
    }

    if (error) {
        return (
            <ProtectedRoute>
                <div className="min-h-screen bg-background p-6">
                    <div className="max-w-4xl mx-auto">
                        <div className="bg-rose-500/10 border border-red-200 rounded-lg p-6">
                            <p className="text-rose-400 mb-4">⚠️ {error}</p>
                            <button
                                onClick={() => fetchIntegrationDetails(parseInt(id || '0'))}
                                className="text-sm text-rose-400 hover:text-red-800"
                            >
                                Try again
                            </button>
                        </div>
                    </div>
                </div>
            </ProtectedRoute>
        );
    }

    if (!integration) {
        return (
            <ProtectedRoute>
                <div className="min-h-screen bg-background p-6">
                    <div className="max-w-4xl mx-auto">
                        <div className="text-center py-12">
                            <div className="text-6xl text-gray-300 mb-4">🔍</div>
                            <p className="text-muted-foreground mb-2">Integration not found</p>
                            <button
                                onClick={() => navigate('/app/integrations')}
                                className="mt-4 bg-cyan-400 text-white px-4 py-2 rounded-md hover:bg-cyan-300"
                            >
                                Back to Marketplace
                            </button>
                        </div>
                    </div>
                </div>
            </ProtectedRoute>
        );
    }

    return (
        <ProtectedRoute>
            <div className="min-h-screen bg-background p-6">
                <div className="max-w-6xl mx-auto">
                    {/* Header */}
                    <div className="flex justify-between items-center mb-6">
                        <div>
                            <h1 className="text-3xl font-bold text-foreground">{integration.name}</h1>
                            <p className="text-muted-foreground mt-1">by Chronos Hub</p>
                        </div>
                        <div className="flex gap-2">
                            <button
                                onClick={() => navigate('/app/integrations')}
                                className="bg-gray-100 text-muted-foreground px-4 py-2 rounded-md hover:bg-gray-200"
                            >
                                ← Back to Marketplace
                            </button>
                            <button
                                onClick={handleInstall}
                                className="bg-cyan-400 text-white px-4 py-2 rounded-md hover:bg-cyan-300"
                            >
                                Install Integration
                            </button>
                        </div>
                    </div>

                    {/* Integration Header */}
                    <div className="bg-card rounded-lg shadow-sm overflow-hidden mb-6">
                        <div className="p-6">
                            <div className="flex flex-col lg:flex-row gap-6">
                                <div className="flex-shrink-0">
                                    <div className="w-20 h-20 bg-blue-100 rounded-xl flex items-center justify-center">
                                        <span className="text-cyan-300 text-4xl">{integration.icon || '🔌'}</span>
                                    </div>
                                </div>

                                <div className="flex-1">
                                    <div className="flex flex-wrap gap-2 mb-3">
                                        <span className="bg-green-100 text-emerald-300 px-3 py-1 rounded-full text-sm">
                                            {integration.category.replace('_', ' ')}
                                        </span>
                                        <span className="bg-blue-100 text-cyan-300 px-3 py-1 rounded-full text-sm">
                                            {integration.integration_type.replace('_', ' ')}
                                        </span>
                                        <span className="bg-gray-100 text-muted-foreground px-3 py-1 rounded-full text-sm">
                                            v{integration.version}
                                        </span>
                                    </div>

                                    <p className="text-muted-foreground mb-4">{integration.description}</p>

                                    <div className="flex flex-wrap gap-6 text-sm text-muted-foreground">
                                        <div className="flex items-center gap-2">
                                            {renderStars(integration.rating)}
                                            <span>{integration.rating.toFixed(1)} ({integration.review_count} reviews)</span>
                                        </div>
                                        <div className="flex items-center gap-1">
                                            📥 {integration.download_count} downloads
                                        </div>
                                        <div className="flex items-center gap-1">
                                            📅 Updated {new Date(integration.updated_at).toLocaleDateString()}
                                        </div>
                                    </div>
                                </div>

                                <div className="flex-shrink-0">
                                    <button
                                        onClick={handleInstall}
                                        className="bg-cyan-400 text-white px-6 py-3 rounded-lg hover:bg-cyan-300 transition-colors w-full lg:w-auto"
                                    >
                                        Install Now
                                    </button>
                                </div>
                            </div>
                        </div>

                        {/* Tabs */}
                        <div className="border-t border-border">
                            <div className="flex">
                                <button
                                    onClick={() => setActiveTab('details')}
                                    className={`flex-1 py-3 px-4 text-sm font-medium ${activeTab === 'details'
                                        ? 'border-b-2 border-blue-600 text-cyan-300'
                                        : 'text-muted-foreground hover:text-muted-foreground'}`}
                                >
                                    Details
                                </button>
                                <button
                                    onClick={() => setActiveTab('setup')}
                                    className={`flex-1 py-3 px-4 text-sm font-medium ${activeTab === 'setup'
                                        ? 'border-b-2 border-blue-600 text-cyan-300'
                                        : 'text-muted-foreground hover:text-muted-foreground'}`}
                                >
                                    Setup Guide
                                </button>
                                <button
                                    onClick={() => setActiveTab('reviews')}
                                    className={`flex-1 py-3 px-4 text-sm font-medium ${activeTab === 'reviews'
                                        ? 'border-b-2 border-blue-600 text-cyan-300'
                                        : 'text-muted-foreground hover:text-muted-foreground'}`}
                                >
                                    Reviews ({integration.review_count})
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Tab Content */}
                    <div className="bg-card rounded-lg shadow-sm p-6">
                        {activeTab === 'details' && (
                            <div>
                                <h3 className="text-xl font-semibold text-foreground mb-4">Integration Details</h3>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                                    <div>
                                        <h4 className="font-medium text-muted-foreground mb-2">Type</h4>
                                        <p className="bg-gray-100 text-muted-foreground px-3 py-2 rounded-md capitalize">
                                            {integration.integration_type.replace('_', ' ')}
                                        </p>
                                    </div>

                                    <div>
                                        <h4 className="font-medium text-muted-foreground mb-2">Category</h4>
                                        <p className="bg-gray-100 text-muted-foreground px-3 py-2 rounded-md capitalize">
                                            {integration.category.replace('_', ' ')}
                                        </p>
                                    </div>

                                    <div>
                                        <h4 className="font-medium text-muted-foreground mb-2">Version</h4>
                                        <p className="bg-gray-100 text-muted-foreground px-3 py-2 rounded-md">
                                            {integration.version}
                                        </p>
                                    </div>

                                    <div>
                                        <h4 className="font-medium text-muted-foreground mb-2">Last Updated</h4>
                                        <p className="bg-gray-100 text-muted-foreground px-3 py-2 rounded-md">
                                            {new Date(integration.updated_at).toLocaleDateString()}
                                        </p>
                                    </div>
                                </div>

                                <div className="mb-6">
                                    <h4 className="font-medium text-muted-foreground mb-2">Supported Features</h4>
                                    <div className="flex flex-wrap gap-2">
                                        {integration.supported_features.map((feature, index) => (
                                            <span key={index} className="bg-blue-100 text-cyan-300 px-3 py-1 rounded-full text-sm">
                                                {feature}
                                            </span>
                                        ))}
                                    </div>
                                </div>

                                <div className="mb-6">
                                    <h4 className="font-medium text-muted-foreground mb-2">Configuration Schema</h4>
                                    <div className="bg-background p-4 rounded-md overflow-x-auto">
                                        <pre className="text-sm text-muted-foreground">
                                            {JSON.stringify(integration.config_schema, null, 2)}
                                        </pre>
                                    </div>
                                </div>

                                {integration.credentials_schema && (
                                    <div className="mb-6">
                                        <h4 className="font-medium text-muted-foreground mb-2">Credentials Schema</h4>
                                        <div className="bg-background p-4 rounded-md overflow-x-auto">
                                            <pre className="text-sm text-muted-foreground">
                                                {JSON.stringify(integration.credentials_schema, null, 2)}
                                            </pre>
                                        </div>
                                    </div>
                                )}

                                <div>
                                    <h4 className="font-medium text-muted-foreground mb-2">Documentation</h4>
                                    {integration.documentation_url ? (
                                        <a
                                            href={integration.documentation_url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-cyan-300 hover:text-blue-800 underline"
                                        >
                                            View Full Documentation
                                        </a>
                                    ) : (
                                        <p className="text-muted-foreground">No documentation available</p>
                                    )}
                                </div>
                            </div>
                        )}

                        {activeTab === 'setup' && (
                            <div>
                                <h3 className="text-xl font-semibold text-foreground mb-4">Setup Guide</h3>

                                <div className="prose max-w-none">
                                    <h4 className="text-lg font-medium text-foreground mb-2">Prerequisites</h4>
                                    <ul className="list-disc pl-6 mb-4 text-muted-foreground">
                                        <li>Chronos AI Agent Builder Studio installed</li>
                                        <li>Valid API credentials for the service</li>
                                        <li>Basic understanding of integration configuration</li>
                                    </ul>

                                    <h4 className="text-lg font-medium text-foreground mb-2">Installation Steps</h4>
                                    <ol className="list-decimal pl-6 mb-4 text-muted-foreground">
                                        <li>Click the "Install Now" button above</li>
                                        <li>Follow the configuration wizard</li>
                                        <li>Enter your API credentials</li>
                                        <li>Configure integration settings</li>
                                        <li>Test the connection</li>
                                        <li>Save and activate the integration</li>
                                    </ol>

                                    <h4 className="text-lg font-medium text-foreground mb-2">Configuration</h4>
                                    <p className="text-muted-foreground mb-4">
                                        After installation, you can configure the integration in your agent settings:
                                    </p>
                                    <ol className="list-decimal pl-6 mb-4 text-muted-foreground">
                                        <li>Go to your agent builder</li>
                                        <li>Select the "Integrations" tab</li>
                                        <li>Find this integration in the list</li>
                                        <li>Click "Configure" to adjust settings</li>
                                        <li>Save your changes</li>
                                    </ol>

                                    <h4 className="text-lg font-medium text-foreground mb-2">Troubleshooting</h4>
                                    <p className="text-muted-foreground mb-4">
                                        If you encounter issues:
                                    </p>
                                    <ul className="list-disc pl-6 mb-4 text-muted-foreground">
                                        <li>Check your API credentials</li>
                                        <li>Verify network connectivity</li>
                                        <li>Review the integration logs</li>
                                        <li>Consult the documentation</li>
                                        <li>Contact support if issues persist</li>
                                    </ul>

                                    <div className="bg-cyan-500/10 border border-blue-200 rounded-lg p-4">
                                        <p className="text-blue-800">
                                            💡 Tip: Use the "Test Connection" button in the configuration wizard to verify your setup before saving.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        )}

                        {activeTab === 'reviews' && (
                            <div>
                                <h3 className="text-xl font-semibold text-foreground mb-4">User Reviews</h3>

                                {/* Write Review */}
                                {!hasReviewed && user && (
                                    <div className="bg-background rounded-lg p-4 mb-6">
                                        <h4 className="font-medium text-muted-foreground mb-3">Write a Review</h4>
                                        <form onSubmit={handleSubmitReview} className="space-y-4">
                                            <div>
                                                <label className="block text-sm font-medium text-muted-foreground mb-1">Rating</label>
                                                {renderEditableStars()}
                                            </div>
                                            <div>
                                                <label htmlFor="comment" className="block text-sm font-medium text-muted-foreground mb-1">
                                                    Your Review
                                                </label>
                                                <textarea
                                                    id="comment"
                                                    value={userReview.comment}
                                                    onChange={(e) => setUserReview({ ...userReview, comment: e.target.value })}
                                                    rows={3}
                                                    className="w-full px-3 py-2 border border-border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                                    placeholder="Share your experience with this integration..."
                                                />
                                            </div>
                                            <button
                                                type="submit"
                                                className="bg-cyan-400 text-white px-4 py-2 rounded-md hover:bg-cyan-300"
                                            >
                                                Submit Review
                                            </button>
                                        </form>
                                    </div>
                                )}

                                {/* Reviews List */}
                                {reviews.length > 0 ? (
                                    <div className="space-y-6">
                                        {reviews.map((review) => (
                                            <div key={review.id} className="border-b border-border pb-6 last:border-b-0">
                                                <div className="flex justify-between items-start mb-2">
                                                    <div className="flex items-center gap-2">
                                                        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                                                            <span className="text-cyan-300 font-medium">
                                                                {review.username.charAt(0).toUpperCase()}
                                                            </span>
                                                        </div>
                                                        <div>
                                                            <p className="font-medium text-foreground">{review.username}</p>
                                                            <p className="text-sm text-muted-foreground">
                                                                {new Date(review.created_at).toLocaleDateString()}
                                                            </p>
                                                        </div>
                                                    </div>
                                                    {renderStars(review.rating)}
                                                </div>
                                                <p className="text-muted-foreground mb-3">{review.comment}</p>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="text-center py-8">
                                        <p className="text-muted-foreground">No reviews yet</p>
                                        <p className="text-sm text-muted-foreground/70 mt-1">Be the first to review this integration!</p>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </ProtectedRoute>
    );
};

export default IntegrationDetailsPage;
