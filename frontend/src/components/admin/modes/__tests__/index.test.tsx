// @vitest-environment jsdom
import { describe, expect, it } from 'vitest'
import { MetaAgentMode } from '../MetaAgentMode'
import { PaymentMode } from '../PaymentMode'
import { PlatformUpdatesMode } from '../PlatformUpdatesMode'
import { SkillsMode } from '../SkillsMode'
import { SupportMode } from '../SupportMode'

describe('admin mode modules', () => {
  it('exports mode components', () => {
    expect(MetaAgentMode).toBeTypeOf('function')
    expect(PaymentMode).toBeTypeOf('function')
    expect(PlatformUpdatesMode).toBeTypeOf('function')
    expect(SkillsMode).toBeTypeOf('function')
    expect(SupportMode).toBeTypeOf('function')
  })
})

