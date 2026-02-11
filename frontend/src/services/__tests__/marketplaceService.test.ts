import { beforeEach, describe, expect, it, vi } from 'vitest'
import { getListing, getListings, installAgent } from '../marketplaceService'

describe('marketplaceService', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('fetches marketplace listings', async () => {
    const payload = { data: [], total: 0, page: 1, page_size: 20 }
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(payload),
    } as unknown as Response)

    const result = await getListings()
    expect((globalThis.fetch as any).mock.calls[0][0]).toContain('/api/marketplace/listings')
    expect(result.total).toBe(0)
  })

  it('fetches one listing', async () => {
    const payload = { id: 11, title: 'Listing' }
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(payload),
    } as unknown as Response)

    const result = await getListing(11)
    expect((globalThis.fetch as any).mock.calls[0][0]).toContain('/api/marketplace/listings/11')
    expect(result.id).toBe(11)
  })

  it('installs a listing by id', async () => {
    const payload = { success: true }
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(payload),
    } as unknown as Response)

    const result = await installAgent(2)
    const [url, options] = (globalThis.fetch as any).mock.calls[0]
    expect(url).toContain('/api/marketplace/listings/2/install')
    expect(options.method).toBe('POST')
    expect(result.success).toBe(true)
  })
})

