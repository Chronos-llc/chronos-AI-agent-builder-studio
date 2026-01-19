import { describe, it, expect, vi } from 'vitest';
import {
  getPlatformUpdates,
  markUpdateAsViewed
} from '../platformUpdatesService';

describe('Platform Updates Service', () => {
  describe('getPlatformUpdates', () => {
    it('should fetch platform updates successfully', async () => {
      const mockData = {
        data: [
          {
            id: '1',
            title: 'New Feature Update',
            content: 'We have released a new feature',
            type: 'feature',
            priority: 'high',
            is_viewed: false
          }
        ],
        total: 1,
        page: 1,
        limit: 10
      };

      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockData)
      });

      global.fetch = mockFetch;

      const result = await getPlatformUpdates();
      
      expect(mockFetch).toHaveBeenCalledWith('/api/platform-updates');
      expect(result).toEqual(mockData);
    });

    it('should handle errors when fetching platform updates', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: false
      });

      global.fetch = mockFetch;

      await expect(getPlatformUpdates()).rejects.toThrow('Failed to fetch platform updates');
    });
  });

  describe('markUpdateAsViewed', () => {
    it('should mark an update as viewed successfully', async () => {
      const updateId = '1';
      
      const mockData = {
        success: true,
        message: 'Update marked as viewed'
      };

      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockData)
      });

      global.fetch = mockFetch;

      const result = await markUpdateAsViewed(updateId);
      
      expect(mockFetch).toHaveBeenCalledWith(`/api/platform-updates/${updateId}/view`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' }
      });
      expect(result).toEqual(mockData);
    });

    it('should handle errors when marking update as viewed', async () => {
      const updateId = '1';
      
      const mockFetch = vi.fn().mockResolvedValue({
        ok: false
      });

      global.fetch = mockFetch;

      await expect(markUpdateAsViewed(updateId)).rejects.toThrow(`Failed to mark update ${updateId} as viewed`);
    });
  });
});
