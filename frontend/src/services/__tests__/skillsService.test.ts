import { beforeEach, describe, expect, it, vi } from 'vitest'
import { getSkill, getSkills, installSkillToAgent } from '../skillsService'

describe('skillsService', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('fetches skills list from the skills endpoint', async () => {
    const payload = { data: [], total: 0, page: 1, page_size: 20 }
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(payload),
    } as unknown as Response)

    const result = await getSkills()

    expect(globalThis.fetch).toHaveBeenCalledTimes(1)
    expect((globalThis.fetch as any).mock.calls[0][0]).toContain('/api/skills/skills')
    expect(result).toEqual(payload)
  })

  it('fetches a single skill by id', async () => {
    const payload = { id: 5, name: 'Example Skill' }
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(payload),
    } as unknown as Response)

    const result = await getSkill(5)
    expect((globalThis.fetch as any).mock.calls[0][0]).toContain('/api/skills/skills/5')
    expect(result.id).toBe(5)
  })

  it('installs a skill to an agent via POST', async () => {
    const payload = { id: 9, agent_id: 22, skill_id: 3 }
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(payload),
    } as unknown as Response)

    const result = await installSkillToAgent(22, { skill_id: 3 })
    const [url, options] = (globalThis.fetch as any).mock.calls[0]

    expect(url).toContain('/api/skills/agents/22/skills')
    expect(options.method).toBe('POST')
    expect(result.agent_id).toBe(22)
  })
})

