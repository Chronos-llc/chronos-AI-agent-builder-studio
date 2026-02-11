import React, { useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { ProtectedRoute } from '../components/ProtectedRoute';

const IntegrationSuccessPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const configId = searchParams.get('config_id');

    useEffect(() => {
        // In a real implementation, you might want to verify the installation
        // or fetch integration details here
    }, [id, configId]);

    const handleContinue = () => {
        navigate('/app/agents');
    };

    const handleConfigure = () => {
        if (id) {
            navigate(`/app/integrations/${id}/configure`);
        }
    };

    return (
        <ProtectedRoute>
            <div className="min-h-screen bg-background p-6">
                <div className="max-w-2xl mx-auto">
                    <div className="bg-card rounded-lg shadow-sm p-8 text-center">
                        <div className="w-16 h-16 bg-emerald-500/15 rounded-full flex items-center justify-center mx-auto mb-4">
                            <span className="text-emerald-300 text-3xl">✅</span>
                        </div>

                        <h1 className="text-2xl font-bold text-foreground mb-2">Integration Installed Successfully!</h1>
                        <p className="text-muted-foreground mb-6">
                            Your integration has been successfully installed and is ready to use.
                        </p>

                        <div className="bg-background rounded-lg p-4 mb-6 text-left">
                            <h3 className="font-medium text-muted-foreground mb-2">What's Next?</h3>
                            <ul className="space-y-2 text-sm text-muted-foreground">
                                <li className="flex items-start gap-2">
                                    <span className="text-emerald-300 mt-0.5">•</span>
                                    <span>Your integration is now available in your agent builder</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <span className="text-emerald-300 mt-0.5">•</span>
                                    <span>Configure the integration settings in your agent</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <span className="text-emerald-300 mt-0.5">•</span>
                                    <span>Test the integration to ensure it works properly</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <span className="text-emerald-300 mt-0.5">•</span>
                                    <span>Monitor usage and performance in your dashboard</span>
                                </li>
                            </ul>
                        </div>

                        <div className="flex flex-col sm:flex-row gap-3 justify-center">
                            <button
                                onClick={handleContinue}
                                className="bg-cyan-400 text-white px-6 py-3 rounded-lg hover:bg-cyan-300 transition-colors font-medium"
                            >
                                Continue to Agent Builder
                            </button>
                            <button
                                onClick={handleConfigure}
                                className="bg-muted text-muted-foreground px-6 py-3 rounded-lg hover:bg-muted transition-colors font-medium"
                            >
                                Configure Integration
                            </button>
                        </div>

                        <div className="mt-6 text-center">
                            <button
                                onClick={() => navigate('/app/integrations')}
                                className="text-sm text-muted-foreground hover:text-foreground"
                            >
                                ← Back to Marketplace
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </ProtectedRoute>
    );
};

export default IntegrationSuccessPage;
