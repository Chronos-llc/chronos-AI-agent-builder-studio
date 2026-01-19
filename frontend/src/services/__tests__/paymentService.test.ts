import { describe, it, expect, vi } from 'vitest';
import {
  getPaymentMethods,
  addPaymentMethod
} from '../paymentService';

describe('Payment Service', () => {
  describe('getPaymentMethods', () => {
    it('should fetch payment methods successfully', async () => {
      const mockData = {
        data: [
          {
            id: '1',
            type: 'credit_card',
            last4: '1234',
            exp_month: 12,
            exp_year: 2024,
            is_default: true
          }
        ]
      };

      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockData)
      });

      global.fetch = mockFetch;

      const result = await getPaymentMethods();
      
      expect(mockFetch).toHaveBeenCalledWith('/api/payment-methods');
      expect(result).toEqual(mockData);
    });

    it('should handle errors when fetching payment methods', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: false
      });

      global.fetch = mockFetch;

      await expect(getPaymentMethods()).rejects.toThrow('Failed to fetch payment methods');
    });
  });

  describe('addPaymentMethod', () => {
    it('should add a payment method successfully', async () => {
      const paymentData = {
        type: 'credit_card',
        card_number: '4111111111111111',
        exp_month: 12,
        exp_year: 2024,
        cvv: '123'
      };

      const mockData = {
        success: true,
        message: 'Payment method added successfully',
        data: {
          id: '1',
          type: 'credit_card',
          last4: '1111',
          exp_month: 12,
          exp_year: 2024,
          is_default: false
        }
      };

      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockData)
      });

      global.fetch = mockFetch;

      const result = await addPaymentMethod(paymentData);
      
      expect(mockFetch).toHaveBeenCalledWith('/api/payment-methods', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(paymentData)
      });
      expect(result).toEqual(mockData);
    });

    it('should handle errors when adding a payment method', async () => {
      const paymentData = {
        type: 'credit_card',
        card_number: '4111111111111111',
        exp_month: 12,
        exp_year: 2024,
        cvv: '123'
      };

      const mockFetch = vi.fn().mockResolvedValue({
        ok: false
      });

      global.fetch = mockFetch;

      await expect(addPaymentMethod(paymentData)).rejects.toThrow('Failed to add payment method');
    });
  });
});
