import { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import { Button } from '../ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../ui/card';
import { Checkbox } from '../ui/checkbox';
import { Loader2, Upload, X, Check, AlertTriangle } from 'lucide-react';
import { MarketplacePublishingForm } from './MarketplacePublishingForm';
import { getCategories, getTags, createListing } from '../../services/marketplaceService';
import type { MarketplaceCategory, MarketplaceTag, MarketplaceListingCreate } from '../../types/marketplace';

interface PublishModalProps {
    agentId: number;
    agentName: string;
    isOpen: boolean;
    onClose: () => void;
    onPublishSuccess: () => void;
}

export const PublishModal = ({
    agentId,
    agentName,
    isOpen,
    onClose,
    onPublishSuccess
}: PublishModalProps) => {
    const [publishToChannels, setPublishToChannels] = useState(true);
    const [publishToMarketplace, setPublishToMarketplace] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [categories, setCategories] = useState<MarketplaceCategory[]>([]);
    const [tags, setTags] = useState<MarketplaceTag[]>([]);
    const [isLoadingCategories, setIsLoadingCategories] = useState(false);
    const [isLoadingTags, setIsLoadingTags] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (publishToMarketplace && isOpen) {
            loadMarketplaceData();
        }
    }, [publishToMarketplace, isOpen]);

    const loadMarketplaceData = async () => {
        try {
            setIsLoadingCategories(true);
            setIsLoadingTags(true);

            const [categoriesResponse, tagsResponse] = await Promise.all([
                getCategories(true),
                getTags(true)
            ]);

            setCategories(categoriesResponse.items);
            setTags(tagsResponse.items);
        } catch (err) {
            console.error('Failed to load marketplace data:', err);
            toast.error('Failed to load marketplace data');
            setError('Failed to load marketplace data. Please try again.');
        } finally {
            setIsLoadingCategories(false);
            setIsLoadingTags(false);
        }
    };

    const handlePublish = async (formData?: MarketplaceListingCreate) => {
        try {
            setIsSubmitting(true);
            setError(null);

            // If publishing to marketplace, create the listing first
            if (publishToMarketplace && formData) {
                const listingData = {
                    ...formData,
                    agent_id: agentId
                };

                await createListing(listingData);
                toast.success('Agent published to marketplace successfully!');
            }

            // If publishing to communication channels
            if (publishToChannels) {
                // In a real implementation, this would call the communication channels API
                // For now, we'll simulate a successful publish
                await new Promise(resolve => setTimeout(resolve, 1000));
                toast.success('Agent published to communication channels successfully!');
            }

            onPublishSuccess();
            onClose();
        } catch (err) {
            console.error('Publish failed:', err);
            toast.error('Failed to publish agent');
            setError(err instanceof Error ? err.message : 'Unknown error occurred');
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleMarketplaceToggle = (checked: boolean) => {
        setPublishToMarketplace(checked);
        if (checked) {
            loadMarketplaceData();
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <Card className="w-full max-w-2xl mx-auto">
                <CardHeader className="flex flex-row items-center justify-between border-b pb-4">
                    <div>
                        <CardTitle>Publish Agent</CardTitle>
                        <CardDescription>Choose where to publish {agentName}</CardDescription>
                    </div>
                    <Button variant="ghost" size="icon" onClick={onClose} disabled={isSubmitting}>
                        <X className="h-4 w-4" />
                    </Button>
                </CardHeader>

                <CardContent className="space-y-6 py-6">
                    {/* Publishing Options */}
                    <div className="space-y-4">
                        <div className="flex items-center space-x-3">
                            <Checkbox
                                id="publish-channels"
                                checked={publishToChannels}
                                onCheckedChange={(checked) => setPublishToChannels(checked as boolean)}
                                disabled={isSubmitting}
                            />
                            <label htmlFor="publish-channels" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                                Publish to Communication Channels
                            </label>
                        </div>

                        <div className="flex items-center space-x-3">
                            <Checkbox
                                id="publish-marketplace"
                                checked={publishToMarketplace}
                                onCheckedChange={handleMarketplaceToggle}
                                disabled={isSubmitting}
                            />
                            <label htmlFor="publish-marketplace" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                                Publish to Marketplace
                            </label>
                        </div>
                    </div>

                    {/* Marketplace Publishing Form */}
                    {publishToMarketplace && (
                        <div className="space-y-4">
                            <h3 className="text-lg font-medium">Marketplace Listing Details</h3>

                            {isLoadingCategories || isLoadingTags ? (
                                <div className="flex justify-center py-8">
                                    <Loader2 className="w-6 h-6 animate-spin text-primary" />
                                </div>
                            ) : (
                                <MarketplacePublishingForm
                                    agentId={agentId}
                                    agentName={agentName}
                                    categories={categories}
                                    tags={tags}
                                    onSubmit={handlePublish}
                                />
                            )}
                        </div>
                    )}

                    {/* Error Display */}
                    {error && (
                        <div className="flex items-center space-x-2 p-3 bg-destructive/10 border border-destructive rounded-md">
                            <AlertTriangle className="w-4 h-4 text-destructive" />
                            <span className="text-sm text-destructive">{error}</span>
                        </div>
                    )}

                    {/* Publish Button */}
                    <div className="flex justify-end space-x-3 pt-4 border-t">
                        <Button
                            variant="outline"
                            onClick={onClose}
                            disabled={isSubmitting}
                        >
                            Cancel
                        </Button>
                        <Button
                            onClick={() => handlePublish()}
                            disabled={isSubmitting || (publishToMarketplace && (isLoadingCategories || isLoadingTags))}
                        >
                            {isSubmitting ? (
                                <>
                                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                    Publishing...
                                </>
                            ) : (
                                <>
                                    <Upload className="w-4 h-4 mr-2" />
                                    Publish Agent
                                </>
                            )}
                        </Button>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};

// Helper component for loading states
const LoadingSkeleton = () => {
    return (
        <div className="space-y-4">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            <div className="h-4 bg-gray-200 rounded w-2/3"></div>
        </div>
    );
};