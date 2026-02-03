"use client"

import { useState } from 'react'
import { MarketplaceListing, Agent, MarketplaceInstallationResponse, CopyStatistics, CopiedAgentsList } from '../types/marketplace'

interface MarketplaceInstallationWithCustomization {
  custom_agent_name?: string
  preserve_original_reference?: boolean
}

export const useMarketplace = () => {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || (typeof window !== 'undefined' ? window.location.origin : 'http://localhost:8000')

  const getListingDetails = async (listingId: number): Promise<MarketplaceListing> => {
    try {
      setIsLoading(true)
      setError(null)
      
      const response = await fetch(`${API_BASE_URL}/api/marketplace/listings/${listingId}`, {
        credentials: 'include'
      })
      
      if (!response.ok) {
        throw new Error(`Failed to fetch listing: ${response.statusText}`)
      }
      
      return await response.json()
    } catch (err) {
      console.error('Error fetching listing details:', err)
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(errorMessage)
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const getAgentDetails = async (agentId: number): Promise<Agent> => {
    try {
      setIsLoading(true)
      setError(null)
      
      const response = await fetch(`${API_BASE_URL}/api/agents/${agentId}`, {
        credentials: 'include'
      })
      
      if (!response.ok) {
        throw new Error(`Failed to fetch agent: ${response.statusText}`)
      }
      
      return await response.json()
    } catch (err) {
      console.error('Error fetching agent details:', err)
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(errorMessage)
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const installMarketplaceAgent = async (
    listingId: number,
    options: MarketplaceInstallationWithCustomization = {}
  ): Promise<MarketplaceInstallationResponse> => {
    try {
      setIsLoading(true)
      setError(null)
      
      const response = await fetch(`${API_BASE_URL}/api/marketplace/listings/${listingId}/install`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          listing_id: listingId,
          custom_agent_name: options.custom_agent_name,
          preserve_original_reference: options.preserve_original_reference !== false
        }),
        credentials: 'include'
      })
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `Failed to install agent: ${response.statusText}`)
      }
      
      const result = await response.json()
      
      return result
    } catch (err) {
      console.error('Error installing marketplace agent:', err)
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(errorMessage)
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const getMyCopiedAgents = async (page: number = 1, pageSize: number = 20): Promise<CopiedAgentsList> => {
    try {
      setIsLoading(true)
      setError(null)
      
      const response = await fetch(`${API_BASE_URL}/api/marketplace/my-copied-agents?page=${page}&page_size=${pageSize}`, {
        credentials: 'include'
      })
      
      if (!response.ok) {
        throw new Error(`Failed to fetch copied agents: ${response.statusText}`)
      }
      
      return await response.json()
    } catch (err) {
      console.error('Error fetching copied agents:', err)
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(errorMessage)
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const getListingCopyStatistics = async (listingId: number): Promise<CopyStatistics> => {
    try {
      setIsLoading(true)
      setError(null)
      
      const response = await fetch(`${API_BASE_URL}/api/marketplace/listings/${listingId}/copy-stats`, {
        credentials: 'include'
      })
      
      if (!response.ok) {
        throw new Error(`Failed to fetch copy statistics: ${response.statusText}`)
      }
      
      return await response.json()
    } catch (err) {
      console.error('Error fetching copy statistics:', err)
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(errorMessage)
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  return {
    isLoading,
    error,
    getListingDetails,
    getAgentDetails,
    installMarketplaceAgent,
    getMyCopiedAgents,
    getListingCopyStatistics
  }
}