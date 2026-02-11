import { describe, it, expect, vi, beforeEach } from 'vitest'
import { phoneNumberService } from '../phoneNumberService'

describe('phoneNumberService', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    Object.defineProperty(globalThis, 'localStorage', {
      value: {
        getItem: vi.fn(() => null),
        setItem: vi.fn(),
        removeItem: vi.fn(),
        clear: vi.fn(),
      },
      configurable: true,
    })
  })

  it('searches numbers with provider endpoint', async () => {
    const mockResponse = [
      {
        provider: 'twilio',
        provider_number_id: 'PN123',
        phone_number_e164: '+14155550100',
        capabilities: ['voice'],
      },
    ]

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockResponse),
    } as unknown as Response)

    const result = await phoneNumberService.searchNumbers(12, 'twilio', {
      country_code: 'US',
      capabilities: ['voice'],
      limit: 20,
    })

    expect(global.fetch).toHaveBeenCalledWith('/api/v1/agents/12/phone/providers/twilio/search', expect.any(Object))
    expect(result[0].phone_number_e164).toBe('+14155550100')
  })

  it('requires ok response when purchasing number', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      json: () => Promise.resolve({ detail: 'provider unavailable' }),
    } as unknown as Response)

    await expect(
      phoneNumberService.purchaseNumber(5, 'vonage', {
        country_code: 'US',
        phone_number_e164: '+14155550111',
        capabilities: ['voice'],
        confirm_purchase: true,
      })
    ).rejects.toThrow('provider unavailable')
  })
})
