import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPaymentMethod, getPaymentMethods } from '../paymentService'

describe('paymentService', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('fetches payment methods', async () => {
    const payload = { data: [], total: 0, page: 1, page_size: 20 }
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(payload),
    } as unknown as Response)

    const result = await getPaymentMethods()
    expect((globalThis.fetch as any).mock.calls[0][0]).toContain('/api/payment/methods')
    expect(result.total).toBe(0)
  })

  it('creates a payment method', async () => {
    const payload = { id: 1, name: 'Card' }
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(payload),
    } as unknown as Response)

    const result = await createPaymentMethod({
      name: 'Card',
      provider: 'stripe',
      configuration: {},
      is_active: true,
    } as any)
    const [url, options] = (globalThis.fetch as any).mock.calls[0]
    expect(url).toContain('/api/payment/methods')
    expect(options.method).toBe('POST')
    expect(result.id).toBe(1)
  })
})

