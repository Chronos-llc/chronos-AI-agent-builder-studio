import { describe, it, expect, vi } from 'vitest';
import {
  createSupportTicket,
  getSupportTickets
} from '../supportService';

describe('Support Service', () => {
  describe('createSupportTicket', () => {
    it('should create a support ticket successfully', async () => {
      const ticketData = {
        subject: 'Test Ticket',
        content: 'This is a test ticket',
        category: 'General Question',
        priority: 'Low',
        attachments: []
      };

      const mockData = {
        success: true,
        message: 'Ticket created successfully',
        data: {
          id: '1',
          subject: 'Test Ticket',
          content: 'This is a test ticket',
          status: 'open'
        }
      };

      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockData)
      });

      global.fetch = mockFetch;

      const result = await createSupportTicket(ticketData);
      
      expect(mockFetch).toHaveBeenCalledWith('/api/support/tickets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(ticketData)
      });
      expect(result).toEqual(mockData);
    });

    it('should handle errors when creating a support ticket', async () => {
      const ticketData = {
        subject: 'Test Ticket',
        content: 'This is a test ticket',
        category: 'General Question',
        priority: 'Low',
        attachments: []
      };

      const mockFetch = vi.fn().mockResolvedValue({
        ok: false
      });

      global.fetch = mockFetch;

      await expect(createSupportTicket(ticketData)).rejects.toThrow('Failed to create support ticket');
    });
  });

  describe('getSupportTickets', () => {
    it('should fetch support tickets successfully', async () => {
      const mockData = {
        data: [
          {
            id: '1',
            subject: 'Test Ticket',
            content: 'This is a test ticket',
            status: 'open',
            priority: 'Low'
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

      const result = await getSupportTickets();
      
      expect(mockFetch).toHaveBeenCalledWith('/api/support/tickets');
      expect(result).toEqual(mockData);
    });

    it('should handle errors when fetching support tickets', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: false
      });

      global.fetch = mockFetch;

      await expect(getSupportTickets()).rejects.toThrow('Failed to fetch support tickets');
    });
  });
});
