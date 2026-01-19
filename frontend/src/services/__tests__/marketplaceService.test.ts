import { describe, it, expect, vi } from 'vitest';
import {
  getMarketplaceListings,
  getAgentDetails,
  installAgent,
  publishAgent
} from '../marketplaceService';

describe('Marketplace Service', () => {
  describe('getMarketplaceListings', () => {
    it('should fetch marketplace listings successfully', async () => {
      const mockData = {
        data: [
          {
            id: '1',
            name: 'Test Agent',
            description: 'This is a test agent',
            category: 'AI Assistants',
            tags: ['test', 'ai']
          }
        ],
        total: 1,
        page: 1,
        limit: 20
      };

      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockData)
      });

      global.fetch = mockFetch;

      const result = await getMarketplaceListings();
      
      expect(mockFetch).toHaveBeenCalledWith('/api/marketplace/agents');
      expect(result).toEqual(mockData);
    });

    it('should handle errors when fetching listings', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: false
      });

      global.fetch = mockFetch;

      await expect(getMarketplaceListings()).rejects.toThrow('Failed to fetch marketplace listings');
    });
  });

  describe('getAgentDetails', () => {
    it('should fetch agent details successfully', async () => {
      const agentId = '1';
      const mockData = {
        id: agentId,
        name: 'Test Agent',
        description: 'This is a test agent',
        category: 'AI Assistants',
        tags: ['test', 'ai']
      };

      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockData)
      });

      global.fetch = mockFetch;

      const result = await getAgentDetails(agentId);
      
      expect(mockFetch).toHaveBeenCalledWith(`/api/marketplace/agents/${agentId}`);
      expect(result).toEqual(mockData);
    });

    it('should handle errors when fetching agent details', async () => {
      const agentId = '1';
      
      const mockFetch = vi.fn().mockResolvedValue({
        ok: false
      });

      global.fetch = mockFetch;

      await expect(getAgentDetails(agentId)).rejects.toThrow(`Failed to fetch agent details for ${agentId}`);
    });
  });

  describe('installAgent', () => {
    it('should install an agent successfully', async () => {
      const agentId = '1';
      const mockData = {
        success: true,
        message: 'Agent installed successfully',
        data: {
          id: agentId,
          name: 'Test Agent',
          version: '1.0.0'
        }
      };

      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockData)
      });

      global.fetch = mockFetch;

      const result = await installAgent(agentId);
      
      expect(mockFetch).toHaveBeenCalledWith(`/api/marketplace/agents/${agentId}/install`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      expect(result).toEqual(mockData);
    });

    it('should handle errors when installing an agent', async () => {
      const agentId = '1';
      
      const mockFetch = vi.fn().mockResolvedValue({
        ok: false
      });

      global.fetch = mockFetch;

      await expect(installAgent(agentId)).rejects.toThrow(`Failed to install agent ${agentId}`);
    });
  });

  describe('publishAgent', () => {
    it('should publish an agent successfully', async () => {
      const publishData = {
        agent_id: '1',
        name: 'Test Agent',
        description: 'This is a test agent',
        category: 'AI Assistants',
        tags: ['test', 'ai'],
        price: 0
      };

      const mockData = {
        success: true,
        message: 'Agent published successfully',
        data: {
          id: '1',
          name: 'Test Agent',
          version: '1.0.0'
        }
      };

      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockData)
      });

      global.fetch = mockFetch;

      const result = await publishAgent(publishData);
      
      expect(mockFetch).toHaveBeenCalledWith('/api/marketplace/agents/publish', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(publishData)
      });
      expect(result).toEqual(mockData);
    });

    it('should handle errors when publishing an agent', async () => {
      const publishData = {
        agent_id: '1',
        name: 'Test Agent',
        description: 'This is a test agent',
        category: 'AI Assistants',
        tags: ['test', 'ai'],
        price: 0
      };

      const mockFetch = vi.fn().mockResolvedValue({
        ok: false
      });

      global.fetch = mockFetch;

      await expect(publishAgent(publishData)).rejects.toThrow('Failed to publish agent');
    });
  });
});
