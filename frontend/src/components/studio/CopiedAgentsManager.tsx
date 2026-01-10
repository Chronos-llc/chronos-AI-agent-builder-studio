"use client"

import React, { useState, useEffect } from 'react'
import { Button } from '../ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '../ui/card'
import { Badge } from '../ui/badge'
import { Input } from '../ui/input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table'
import { Skeleton } from '../ui/skeleton'
import { Separator } from '../ui/separator'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '../ui/dropdown-menu'
import { MoreHorizontal, Search, Filter, Loader2 } from 'lucide-react'
import { toast } from '../ui/use-toast'
import { useMarketplace } from '../../hooks/useMarketplace'
import { useRouter } from 'next/navigation'

interface CopiedAgent {
    agent_id: number
    name: string
    description: string
    status: string
    created_at: string
    updated_at: string
    listing_id: number
    listing_title: string
    original_agent_id: number
    installed_at: string
    author_id: number
    is_copy: boolean
    metadata: Record<string, any>
}

export default function CopiedAgentsManager() {
    const [copiedAgents, setCopiedAgents] = useState<CopiedAgent[]>([])
    const [isLoading, setIsLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [searchTerm, setSearchTerm] = useState('')
    const [filterType, setFilterType] = useState<'all' | 'recent' | 'popular'>('all')
    const [currentPage, setCurrentPage] = useState(1)
    const [pageSize] = useState(10)
    const [selectedAgent, setSelectedAgent] = useState<CopiedAgent | null>(null)
    const { getMyCopiedAgents } = useMarketplace()
    const router = useRouter()

    useEffect(() => {
        const fetchCopiedAgents = async () => {
            try {
                setIsLoading(true)
                setError(null)

                const data = await getMyCopiedAgents(currentPage, pageSize)
                setCopiedAgents(data.items || [])

            } catch (err) {
                console.error('Failed to fetch copied agents:', err)
                setError('Failed to load copied agents')
                toast({
                    title: 'Error',
                    description: 'Failed to load copied agents',
                    variant: 'destructive'
                })
            } finally {
                setIsLoading(false)
            }
        }

        fetchCopiedAgents()
    }, [currentPage, pageSize, getMyCopiedAgents])

    const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setSearchTerm(e.target.value)
    }

    const handleFilterChange = (type: 'all' | 'recent' | 'popular') => {
        setFilterType(type)
    }

    const handleViewAgent = (agent: CopiedAgent) => {
        setSelectedAgent(agent)
    }

    const handleBackToList = () => {
        setSelectedAgent(null)
    }

    const handleNavigateToAgent = (agentId: number) => {
        router.push(`/studio/agents/${agentId}`)
    }

    const filteredAgents = copiedAgents.filter(agent => {
        // Search filter
        const matchesSearch = agent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            agent.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
            agent.listing_title.toLowerCase().includes(searchTerm.toLowerCase())

        // Type filter
        let matchesFilter = true
        if (filterType === 'recent') {
            const oneWeekAgo = new Date()
            oneWeekAgo.setDate(oneWeekAgo.getDate() - 7)
            matchesFilter = new Date(agent.installed_at) >= oneWeekAgo
        } else if (filterType === 'popular') {
            // For popular, we could filter by usage or ratings in a real implementation
            matchesFilter = true // Placeholder
        }

        return matchesSearch && matchesFilter
    })

    const getAgentStatusBadge = (status: string) => {
        switch (status.toLowerCase()) {
            case 'active':
                return <Badge variant="success">Active</Badge>
            case 'inactive':
                return <Badge variant="secondary">Inactive</Badge>
            case 'draft':
                return <Badge variant="outline">Draft</Badge>
            case 'archived':
                return <Badge variant="destructive">Archived</Badge>
            default:
                return <Badge variant="default">{status}</Badge>
        }
    }

    if (isLoading && !copiedAgents.length) {
        return (
            <Card className="w-full">
                <CardHeader>
                    <CardTitle>My Copied Agents</CardTitle>
                    <CardDescription>Manage agents you've copied from the marketplace</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        <div className="flex justify-between items-center mb-4">
                            <Skeleton className="h-10 w-64" />
                            <div className="flex gap-2">
                                <Skeleton className="h-10 w-24" />
                                <Skeleton className="h-10 w-24" />
                            </div>
                        </div>
                        <Skeleton className="h-8 w-full" />
                        <Skeleton className="h-64 w-full" />
                    </div>
                </CardContent>
            </Card>
        )
    }

    if (error) {
        return (
            <Card className="w-full">
                <CardHeader>
                    <CardTitle>My Copied Agents</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-center py-8">
                        <p className="text-red-500 mb-4">{error}</p>
                        <Button
                            onClick={() => window.location.reload()}
                            variant="outline"
                        >
                            Retry
                        </Button>
                    </div>
                </CardContent>
            </Card>
        )
    }

    if (selectedAgent) {
        return (
            <Card className="w-full">
                <CardHeader>
                    <div className="flex justify-between items-center">
                        <div>
                            <CardTitle>{selectedAgent.name}</CardTitle>
                            <CardDescription className="mt-2">
                                Copied from: {selectedAgent.listing_title}
                            </CardDescription>
                        </div>
                        <Button onClick={handleBackToList} variant="outline" size="sm">
                            Back to List
                        </Button>
                    </div>
                </CardHeader>

                <CardContent>
                    <Tabs defaultValue="details" className="w-full">
                        <TabsList className="mb-4">
                            <TabsTrigger value="details">Agent Details</TabsTrigger>
                            <TabsTrigger value="original">Original Listing</TabsTrigger>
                            <TabsTrigger value="metadata">Copy Metadata</TabsTrigger>
                        </TabsList>

                        <TabsContent value="details">
                            <div className="space-y-6">
                                <div>
                                    <h3 className="font-semibold mb-2">Description</h3>
                                    <p className="text-muted-foreground">
                                        {selectedAgent.description || 'No description provided.'}
                                    </p>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <h3 className="font-semibold mb-2">Agent Information</h3>
                                        <div className="space-y-2 text-sm">
                                            <div className="flex justify-between">
                                                <span className="text-muted-foreground">Status</span>
                                                {getAgentStatusBadge(selectedAgent.status)}
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-muted-foreground">Agent ID</span>
                                                <span>{selectedAgent.agent_id}</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-muted-foreground">Created</span>
                                                <span>{new Date(selectedAgent.created_at).toLocaleString()}</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-muted-foreground">Updated</span>
                                                <span>{new Date(selectedAgent.updated_at).toLocaleString()}</span>
                                            </div>
                                        </div>
                                    </div>

                                    <div>
                                        <h3 className="font-semibold mb-2">Copy Information</h3>
                                        <div className="space-y-2 text-sm">
                                            <div className="flex justify-between">
                                                <span className="text-muted-foreground">Copied From</span>
                                                <span>{selectedAgent.listing_title}</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-muted-foreground">Original Agent ID</span>
                                                <span>{selectedAgent.original_agent_id}</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-muted-foreground">Install Date</span>
                                                <span>{new Date(selectedAgent.installed_at).toLocaleString()}</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-muted-foreground">Listing ID</span>
                                                <span>{selectedAgent.listing_id}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </TabsContent>

                        <TabsContent value="original">
                            <div className="space-y-4">
                                <h3 className="font-semibold mb-2">Original Marketplace Listing</h3>
                                <div className="space-y-2 text-sm">
                                    <div>
                                        <span className="text-muted-foreground font-medium">Title: </span>
                                        <span>{selectedAgent.listing_title}</span>
                                    </div>
                                    <div>
                                        <span className="text-muted-foreground font-medium">Listing ID: </span>
                                        <span>{selectedAgent.listing_id}</span>
                                    </div>
                                    <div>
                                        <span className="text-muted-foreground font-medium">Author ID: </span>
                                        <span>{selectedAgent.author_id}</span>
                                    </div>
                                    <div>
                                        <span className="text-muted-foreground font-medium">Installed: </span>
                                        <span>{new Date(selectedAgent.installed_at).toLocaleString()}</span>
                                    </div>
                                </div>

                                <Button
                                    onClick={() => router.push(`/marketplace/listings/${selectedAgent.listing_id}`)}
                                    variant="outline"
                                    size="sm"
                                    className="mt-4"
                                >
                                    View Original Listing
                                </Button>
                            </div>
                        </TabsContent>

                        <TabsContent value="metadata">
                            <div className="space-y-4">
                                <h3 className="font-semibold mb-2">Copy Metadata</h3>
                                {selectedAgent.metadata && selectedAgent.metadata.marketplace_copy ? (
                                    <pre className="bg-muted p-4 rounded text-sm overflow-auto max-h-96">
                                        {JSON.stringify(selectedAgent.metadata.marketplace_copy, null, 2)}
                                    </pre>
                                ) : (
                                    <p className="text-muted-foreground">No copy metadata available.</p>
                                )}
                            </div>
                        </TabsContent>
                    </Tabs>
                </CardContent>

                <CardFooter className="flex justify-end gap-2">
                    <Button
                        onClick={() => handleNavigateToAgent(selectedAgent.agent_id)}
                        variant="default"
                    >
                        View Full Agent
                    </Button>
                    <Button
                        onClick={() => router.push(`/studio/agents/${selectedAgent.agent_id}/edit`)}
                        variant="secondary"
                    >
                        Edit Agent
                    </Button>
                </CardFooter>
            </Card>
        )
    }

    return (
        <Card className="w-full">
            <CardHeader>
                <CardTitle>My Copied Agents</CardTitle>
                <CardDescription>Manage and view agents you've copied from the marketplace</CardDescription>
            </CardHeader>

            <CardContent>
                <div className="flex flex-col md:flex-row justify-between items-center gap-4 mb-6">
                    <div className="relative w-full md:w-auto flex-1">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <Input
                            type="search"
                            placeholder="Search copied agents..."
                            value={searchTerm}
                            onChange={handleSearchChange}
                            className="pl-10 w-full md:w-64"
                        />
                    </div>

                    <div className="flex items-center gap-2">
                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <Button variant="outline" className="gap-2">
                                    <Filter className="h-4 w-4" />
                                    {filterType === 'all' && 'All Agents'}
                                    {filterType === 'recent' && 'Recent'}
                                    {filterType === 'popular' && 'Popular'}
                                </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                                <DropdownMenuItem onClick={() => handleFilterChange('all')}>All Agents</DropdownMenuItem>
                                <DropdownMenuItem onClick={() => handleFilterChange('recent')}>Recently Copied</DropdownMenuItem>
                                <DropdownMenuItem onClick={() => handleFilterChange('popular')}>Popular</DropdownMenuItem>
                            </DropdownMenuContent>
                        </DropdownMenu>
                    </div>
                </div>

                {isLoading ? (
                    <div className="space-y-3">
                        <Skeleton className="h-10 w-full" />
                        <Skeleton className="h-10 w-full" />
                        <Skeleton className="h-10 w-full" />
                    </div>
                ) : (
                    <>
                        {filteredAgents.length === 0 ? (
                            <div className="text-center py-8">
                                <p className="text-muted-foreground mb-4">No copied agents found.</p>
                                <Button
                                    onClick={() => router.push('/marketplace')}
                                    variant="outline"
                                >
                                    Browse Marketplace
                                </Button>
                            </div>
                        ) : (
                            <div className="overflow-x-auto">
                                <Table>
                                    <TableHeader>
                                        <TableRow>
                                            <TableHead>Agent Name</TableHead>
                                            <TableHead>Original Listing</TableHead>
                                            <TableHead>Status</TableHead>
                                            <TableHead>Copied On</TableHead>
                                            <TableHead className="text-right">Actions</TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {filteredAgents.map((agent) => (
                                            <TableRow key={agent.agent_id} className="hover:bg-muted/50">
                                                <TableCell className="font-medium max-w-xs truncate">
                                                    {agent.name}
                                                </TableCell>
                                                <TableCell className="max-w-xs truncate">
                                                    {agent.listing_title}
                                                </TableCell>
                                                <TableCell>
                                                    {getAgentStatusBadge(agent.status)}
                                                </TableCell>
                                                <TableCell>
                                                    {new Date(agent.installed_at).toLocaleDateString()}
                                                </TableCell>
                                                <TableCell className="text-right">
                                                    <DropdownMenu>
                                                        <DropdownMenuTrigger asChild>
                                                            <Button variant="ghost" className="h-8 w-8 p-0">
                                                                <span className="sr-only">Open menu</span>
                                                                <MoreHorizontal className="h-4 w-4" />
                                                            </Button>
                                                        </DropdownMenuTrigger>
                                                        <DropdownMenuContent align="end">
                                                            <DropdownMenuItem onClick={() => handleViewAgent(agent)}>
                                                                View Details
                                                            </DropdownMenuItem>
                                                            <DropdownMenuItem onClick={() => handleNavigateToAgent(agent.agent_id)}>
                                                                View Full Agent
                                                            </DropdownMenuItem>
                                                            <DropdownMenuItem onClick={() => router.push(`/studio/agents/${agent.agent_id}/edit`)}>
                                                                Edit Agent
                                                            </DropdownMenuItem>
                                                            <DropdownMenuItem onClick={() => router.push(`/marketplace/listings/${agent.listing_id}`)}>
                                                                View Original Listing
                                                            </DropdownMenuItem>
                                                        </DropdownMenuContent>
                                                    </DropdownMenu>
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            </div>
                        )}
                    </>
                )}
            </CardContent>

            {filteredAgents.length > 0 && (
                <CardFooter className="flex justify-between items-center">
                    <div className="text-sm text-muted-foreground">
                        Showing {filteredAgents.length} of {copiedAgents.length} copied agents
                    </div>
                    <div className="flex gap-2">
                        <Button
                            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                            disabled={currentPage === 1 || isLoading}
                            variant="outline"
                            size="sm"
                        >
                            Previous
                        </Button>
                        <Button
                            onClick={() => setCurrentPage(p => p + 1)}
                            disabled={copiedAgents.length < pageSize || isLoading}
                            variant="outline"
                            size="sm"
                        >
                            Next
                        </Button>
                    </div>
                </CardFooter>
            )}
        </Card>
    )
}