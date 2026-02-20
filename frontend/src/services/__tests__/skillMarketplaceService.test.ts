import { beforeEach, describe, expect, it, vi } from 'vitest'
import { skillMarketplaceService } from '../skillMarketplaceService'

describe('skillMarketplaceService', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('loads marketplace list from canonical endpoint', async () => {
    const payload = { items: [], total: 0, page: 1, page_size: 20, has_more: false }
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(payload),
    } as unknown as Response)

    const response = await skillMarketplaceService.listMarketplace()
    const [url] = (globalThis.fetch as unknown as { mock: { calls: unknown[][] } }).mock.calls[0]

    expect(url).toContain('/api/skills/marketplace')
    expect(response.total).toBe(0)
  })

  it('calls install endpoint with payload', async () => {
    const payload = { success: true, message: 'ok', target_type: 'agent', target_id: 1, installation_id: 2 }
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(payload),
    } as unknown as Response)

    const response = await skillMarketplaceService.installSkill(8, { target_type: 'agent', agent_id: 12 })
    const [url, options] = (globalThis.fetch as unknown as { mock: { calls: unknown[][] } }).mock.calls[0]

    expect(url).toContain('/api/skills/marketplace/8/install')
    expect((options as RequestInit).method).toBe('POST')
    expect(response.success).toBe(true)
  })

  it('calls admin submissions queue endpoint', async () => {
    const payload = { items: [], total: 0 }
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(payload),
    } as unknown as Response)

    const response = await skillMarketplaceService.listSubmissions()
    const [url] = (globalThis.fetch as unknown as { mock: { calls: unknown[][] } }).mock.calls[0]

    expect(url).toContain('/api/skills/admin/submissions')
    expect(response.total).toBe(0)
  })
})
