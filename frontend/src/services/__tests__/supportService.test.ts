import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createSupportMessage, getSupportMessages } from '../supportService'

describe('supportService', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('fetches support messages', async () => {
    const payload = { data: [], total: 0, page: 1, page_size: 20 }
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(payload),
    } as unknown as Response)

    const result = await getSupportMessages()
    expect((globalThis.fetch as any).mock.calls[0][0]).toContain('/api/support/messages')
    expect(result.total).toBe(0)
  })

  it('creates a support message', async () => {
    const payload = { id: 1, subject: 'Need help' }
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(payload),
    } as unknown as Response)

    const result = await createSupportMessage({
      subject: 'Need help',
      message: 'Issue details',
      priority: 'NORMAL' as any,
      category: 'TECHNICAL' as any,
    })
    const [url, options] = (globalThis.fetch as any).mock.calls[0]
    expect(url).toContain('/api/support/messages')
    expect(options.method).toBe('POST')
    expect(result.id).toBe(1)
  })
})

