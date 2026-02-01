"use client"

import { useState, useEffect } from 'react'
import { Button } from '../ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '../ui/card'
import { Badge } from '../ui/badge'
import { Skeleton } from '../ui/skeleton'
import { Separator } from '../ui/separator'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs'
import { Agent, MarketplaceListing } from '../../types/marketplace'
import { useMarketplace } from '../../hooks/useMarketplace'
import AgentCopyModal from './AgentCopyModal'
import { toast } from '../ui/use-toast'

interface MarketplaceAgentViewerProps {
  listingId: number
  onCopySuccess?: (agentId: number) => void
  showCopyButton?: boolean
}

export default function MarketplaceAgentViewer({ 
  listingId, 
  onCopySuccess, 
  showCopyButton = true 
}: MarketplaceAgentViewerProps) {
  const [listing, setListing] = useState<MarketplaceListing | null>(null)
  const [originalAgent, setOriginalAgent] = useState<Agent | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isCopyModalOpen, setIsCopyModalOpen] = useState(false)
  const { getListingDetails, getAgentDetails } = useMarketplace()

  useEffect(() => {
    const fetchListingAndAgent = async () => {
      try {
        setIsLoading(true)
        setError(null)
        
        // Fetch marketplace listing
        const listingData = await getListingDetails(listingId)
        setListing(listingData)
        
        // Fetch original agent details
        if (listingData.agent_id) {
          const agentData = await getAgentDetails(listingData.agent_id)
          setOriginalAgent(agentData)
        }
        
      } catch (err) {
        console.error('Failed to fetch marketplace agent details:', err)
        setError('Failed to load marketplace agent details')
        toast({
          title: 'Error',
          description: 'Failed to load marketplace agent details',
          variant: 'destructive'
        })
      } finally {
        setIsLoading(false)
      }
    }
    
    fetchListingAndAgent()
  }, [listingId, getListingDetails, getAgentDetails])

  const handleCopyClick = () => {
    setIsCopyModalOpen(true)
  }

  const handleCopySuccess = (agentId: number) => {
    setIsCopyModalOpen(false)
    if (onCopySuccess) {
      onCopySuccess(agentId)
    }
    toast({
      title: 'Success',
      description: 'Agent copied successfully to your agents!',
      variant: 'success'
    })
  }

  if (isLoading) {
    return (
      <Card className="w-full max-w-4xl">
        <CardHeader>
          <Skeleton className="h-8 w-3/4" />
          <Skeleton className="h-4 w-1/2" />
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
            <Skeleton className="h-4 w-4/6" />
            <Separator />
            <div className="grid grid-cols-2 gap-4">
              <Skeleton className="h-6 w-24" />
              <Skeleton className="h-6 w-24" />
            </div>
          </div>
        </CardContent>
        <CardFooter>
          <Skeleton className="h-10 w-32" />
        </CardFooter>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="w-full max-w-4xl">
        <CardHeader>
          <CardTitle>Error Loading Agent</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-red-500">{error}</p>
        </CardContent>
      </Card>
    )
  }

  if (!listing) {
    return (
      <Card className="w-full max-w-4xl">
        <CardHeader>
          <CardTitle>Agent Not Found</CardTitle>
        </CardHeader>
        <CardContent>
          <p>The requested marketplace agent could not be found.</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="w-full max-w-4xl">
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="text-2xl font-bold">{listing.title}</CardTitle>
            <CardDescription className="mt-2 text-lg">{listing.description}</CardDescription>
          </div>
          {showCopyButton && (
            <Button 
              onClick={handleCopyClick} 
              className="bg-primary hover:bg-primary/90"
              size="lg"
            >
              Copy to My Agents
            </Button>
          )}
        </div>
      </CardHeader>

      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          {/* Agent Info */}
          <div className="md:col-span-2">
            <div className="flex items-center gap-2 mb-4">
               <Badge variant="secondary" className="text-sm">
                {listing.listing_type}
              </Badge>
              <Badge variant="outline" className="text-sm">
                {listing.category?.display_name || listing.category?.name || 'General'}
              </Badge>
              {listing.tags && listing.tags.length > 0 && (
                <div className="flex gap-1 flex-wrap">
                  {listing.tags.slice(0, 3).map((tag) => (
                    <Badge key={tag} variant="outline" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                </div>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div>
                <p className="text-sm text-muted-foreground">Author</p>
                <p className="font-medium">{listing.author_name || 'Unknown Author'}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Version</p>
                <p className="font-medium">{listing.version || '1.0.0'}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Installs</p>
                <p className="font-medium">{listing.install_count || 0}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Rating</p>
                <p className="font-medium">
                  {listing.rating_average ? `${listing.rating_average}/5` : 'Not rated'}
                </p>
              </div>
            </div>
          </div>

          {/* Stats */}
          <div className="border-l pl-6">
            <h3 className="font-semibold mb-3">Statistics</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Views</span>
                <span className="font-medium">{listing.view_count || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Reviews</span>
                <span className="font-medium">{listing.rating_count || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Published</span>
                <span className="font-medium">
                  {listing.published_at ? new Date(listing.published_at).toLocaleDateString() : 'N/A'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Agent Details Tabs */}
        <Tabs defaultValue="overview" className="mt-6">
          <TabsList className="mb-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="configuration">Configuration</TabsTrigger>
            <TabsTrigger value="features">Features</TabsTrigger>
            {originalAgent && <TabsTrigger value="original">Original Agent</TabsTrigger>}
          </TabsList>

          <TabsContent value="overview">
            <div className="space-y-4">
              <h4 className="font-semibold text-lg">About This Agent</h4>
              <p className="text-muted-foreground">
                {listing.description || 'No description provided.'}
              </p>

              {listing.preview_images && listing.preview_images.length > 0 && (
                <div className="mt-6">
                  <h4 className="font-semibold mb-3">Preview Images</h4>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {listing.preview_images.map((image, index) => (
                      <img 
                        key={index} 
                        src={image} 
                        alt={`Preview ${index + 1}`} 
                        className="rounded-lg border aspect-video object-cover"
                      />
                    ))}
                  </div>
                </div>
              )}

              {listing.demo_video_url && (
                <div className="mt-6">
                  <h4 className="font-semibold mb-3">Demo Video</h4>
                  <div className="aspect-video bg-muted rounded-lg overflow-hidden">
                    <iframe 
                      src={listing.demo_video_url} 
                      title="Agent Demo Video" 
                      className="w-full h-full"
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                      allowFullScreen
                    />
                  </div>
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="configuration">
            <div className="space-y-4">
              <h4 className="font-semibold text-lg">Agent Configuration</h4>
              {originalAgent ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h5 className="font-medium mb-2">Model Configuration</h5>
                    <pre className="bg-muted p-3 rounded text-sm overflow-auto max-h-64">
                      {JSON.stringify(originalAgent.model_config || {}, null, 2)}
                    </pre>
                  </div>
                  <div>
                    <h5 className="font-medium mb-2">System Prompt</h5>
                    <div className="bg-muted p-3 rounded text-sm max-h-64 overflow-auto">
                      {originalAgent.system_prompt || 'No system prompt configured.'}
                    </div>
                  </div>
                </div>
              ) : (
                <p className="text-muted-foreground">Configuration details not available.</p>
              )}
            </div>
          </TabsContent>

          <TabsContent value="features">
            <div className="space-y-4">
              <h4 className="font-semibold text-lg">Agent Features</h4>
              {originalAgent ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {originalAgent.tags && originalAgent.tags.length > 0 && (
                    <div>
                      <h5 className="font-medium mb-2">Capabilities</h5>
                      <div className="flex flex-wrap gap-2">
                        {originalAgent.tags.map((tag, index) => (
                          <Badge key={index} variant="secondary">{tag}</Badge>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {originalAgent.sub_agent_config && (
                    <div>
                      <h5 className="font-medium mb-2">Sub-Agent Configuration</h5>
                      <div className="space-y-2">
                        {(() => {
                          const subAgentConfig = originalAgent.sub_agent_config!;
                          return Object.keys(subAgentConfig).map((subAgentKey) => {
                            const subAgent = subAgentConfig[subAgentKey];
                            // Check if subAgent has enabled property
                            const isEnabled = subAgent && typeof subAgent === 'object' && 'enabled' in subAgent ? Boolean(subAgent.enabled) : false;
                            
                            return (
                              <div key={subAgentKey} className="flex items-center gap-2">
                                <span className="capitalize">{subAgentKey.replace('_agent', '')}</span>
                                <Badge variant={isEnabled ? 'success' : 'secondary'}>
                                  {isEnabled ? 'Enabled' : 'Disabled'}
                                </Badge>
                              </div>
                            );
                          });
                        })()}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-muted-foreground">Feature information not available.</p>
              )}
            </div>
          </TabsContent>

          {originalAgent && (
            <TabsContent value="original">
              <div className="space-y-4">
                <h4 className="font-semibold text-lg">Original Agent Details</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h5 className="font-medium mb-2">Agent Information</h5>
                    <div className="space-y-2 text-sm">
                      <div>
                        <span className="text-muted-foreground">Name: </span>
                        <span className="font-medium">{originalAgent.name}</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">ID: </span>
                        <span className="font-medium">{originalAgent.id}</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Status: </span>
                        <Badge variant="outline" className="ml-2">{originalAgent.status}</Badge>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Created: </span>
                        <span className="font-medium">
                          {new Date(originalAgent.created_at).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div>
                    <h5 className="font-medium mb-2">Usage Statistics</h5>
                    <div className="space-y-2 text-sm">
                      <div>
                        <span className="text-muted-foreground">Usage Count: </span>
                        <span className="font-medium">{originalAgent.usage_count}</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Success Rate: </span>
                        <span className="font-medium">{originalAgent.success_rate}%</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Avg Response Time: </span>
                        <span className="font-medium">{originalAgent.avg_response_time}s</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </TabsContent>
          )}
        </Tabs>
      </CardContent>

      <CardFooter className="flex justify-between items-center">
        <div className="text-sm text-muted-foreground">
          Listing ID: {listing.id}
        </div>
        {showCopyButton && (
          <Button 
            onClick={handleCopyClick} 
            variant="secondary"
            size="sm"
          >
            Copy Agent
          </Button>
        )}
      </CardFooter>

      {/* Copy Modal */}
      <AgentCopyModal
        isOpen={isCopyModalOpen}
        onClose={() => setIsCopyModalOpen(false)}
        listingId={listingId}
        listingTitle={listing.title}
        originalAgentName={originalAgent?.name || listing.title}
        onCopySuccess={handleCopySuccess}
      />
    </Card>
  )
}