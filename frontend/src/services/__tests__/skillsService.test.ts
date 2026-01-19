import { describe, it, expect, vi } from 'vitest';
import {
  getSkillsList,
  getSkillDetails,
  installSkill
} from '../skillsService';

describe('Skills Service', () => {
  describe('getSkillsList', () => {
    it('should fetch skills list successfully', async () => {
      const mockData = {
        data: [
          {
            id: '1',
            name: 'Test Skill',
            description: 'This is a test skill',
            category: 'Productivity',
            version: '1.0.0'
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

      const result = await getSkillsList();
      
      expect(mockFetch).toHaveBeenCalledWith('/api/skills');
      expect(result).toEqual(mockData);
    });

    it('should handle errors when fetching skills list', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: false
      });

      global.fetch = mockFetch;

      await expect(getSkillsList()).rejects.toThrow('Failed to fetch skills list');
    });
  });

  describe('getSkillDetails', () => {
    it('should fetch skill details successfully', async () => {
      const skillId = '1';
      const mockData = {
        id: skillId,
        name: 'Test Skill',
        description: 'This is a test skill',
        category: 'Productivity',
        version: '1.0.0'
      };

      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockData)
      });

      global.fetch = mockFetch;

      const result = await getSkillDetails(skillId);
      
      expect(mockFetch).toHaveBeenCalledWith(`/api/skills/${skillId}`);
      expect(result).toEqual(mockData);
    });

    it('should handle errors when fetching skill details', async () => {
      const skillId = '1';
      
      const mockFetch = vi.fn().mockResolvedValue({
        ok: false
      });

      global.fetch = mockFetch;

      await expect(getSkillDetails(skillId)).rejects.toThrow(`Failed to fetch skill details for ${skillId}`);
    });
  });

  describe('installSkill', () => {
    it('should install a skill successfully', async () => {
      const skillId = '1';
      const agentId = '1';
      
      const mockData = {
        success: true,
        message: 'Skill installed successfully',
        data: {
          id: skillId,
          name: 'Test Skill',
          version: '1.0.0'
        }
      };

      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockData)
      });

      global.fetch = mockFetch;

      const result = await installSkill(skillId, agentId);
      
      expect(mockFetch).toHaveBeenCalledWith(`/api/skills/${skillId}/install`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agent_id: agentId })
      });
      expect(result).toEqual(mockData);
    });

    it('should handle errors when installing a skill', async () => {
      const skillId = '1';
      const agentId = '1';
      
      const mockFetch = vi.fn().mockResolvedValue({
        ok: false
      });

      global.fetch = mockFetch;

      await expect(installSkill(skillId, agentId)).rejects.toThrow(`Failed to install skill ${skillId}`);
    });
  });
});
