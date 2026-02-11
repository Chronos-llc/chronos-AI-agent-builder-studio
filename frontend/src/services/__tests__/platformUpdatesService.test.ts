import { beforeEach, describe, expect, it, vi } from 'vitest'
import { getPlatformUpdates, markUpdateViewed } from '../platformUpdatesService'

describe('platformUpdatesService', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('fetches platform updates list', async () => {
    const payload = { data: [], total: 0, page: 1, page_size: 20 }
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(payload),
    } as unknown as Response)

    const result = await getPlatformUpdates()
    expect((globalThis.fetch as any).mock.calls[0][0]).toContain('/api/updates')
    expect(result.total).toBe(0)
  })

  it('marks an update as viewed', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({}),
    } as unknown as Response)

    await markUpdateViewed(3)
    const [url, options] = (globalThis.fetch as any).mock.calls[0]
    expect(url).toContain('/api/updates/3/mark-viewed')
    expect(options.method).toBe('POST')
  })
})

