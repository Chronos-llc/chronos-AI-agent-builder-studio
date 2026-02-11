export type PricingPlan = {
  id: 'payg' | 'lite' | 'lotus' | 'special' | 'enterprise'
  name: string
  subtitle?: string
  priceLabel: string
  ctaLabel: string
  ctaHref: string
  highlight?: boolean
  features: string[]
  note?: string
}

export const PRICING_PLANS: PricingPlan[] = [
  {
    id: 'payg',
    name: 'Pay-as-you-go',
    subtitle: 'Start for free',
    priceLabel: '$0 + AI Spend / mo  (NGN 0)',
    ctaLabel: 'Start for free',
    ctaHref: '/app',
    features: [
      'Agent Builder studio with Fuzzy-assisted setup',
      'Agent Suite chat and conversation history',
      'Workflow generator for no-code/low-code automations',
      'Core model pickers and provider catalog access',
      'Integrations Hub installs (community connectors)',
      'Community support',
    ],
    note: 'Usage is billed at provider cost for model/API consumption.',
  },
  {
    id: 'lite',
    name: 'Lite',
    priceLabel: '$85 + AI Spend / mo',
    ctaLabel: 'Upgrade to Lite',
    ctaHref: '/login',
    highlight: true,
    features: [
      'All Pay-as-you-go features',
      'Advanced Voice Studio controls (STT/TTS/voice pickers)',
      'Marketplace publishing and copy/install workflows',
      'Context tracking and condensed conversation memory',
      'Virtual computer controls and sandbox test tooling',
      'Priority live chat support',
    ],
  },
  {
    id: 'lotus',
    name: 'Lotus',
    subtitle: 'Special plan for power users: Team/Developers',
    priceLabel: '$395 + AI Spend / mo',
    ctaLabel: 'Get Lotus',
    ctaHref: '/login',
    features: [
      'All Lite features',
      'Team/developer collaboration workflows',
      'Advanced orchestration controls across sub-agents',
      'Workflow execution logs and export-ready traces',
      'Higher operational limits for agent runs and integrations',
      'Enhanced support response times',
    ],
  },
  {
    id: 'special',
    name: 'Special Service',
    subtitle: 'Premium management from the Chronos team',
    priceLabel: 'Contact team',
    ctaLabel: 'Contact team',
    ctaHref: '/login',
    features: [
      'All Lotus features',
      'Managed rollout and continuous optimization by our team',
      'Integration architecture and deployment guidance',
      'Monthly strategy and performance reviews',
      'Priority escalation path',
    ],
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    priceLabel: 'Contact team',
    ctaLabel: 'Contact sales',
    ctaHref: '/login',
    features: [
      'All Lotus features',
      'White-glove onboarding',
      'Custom workspace limits and governance controls',
      'Dedicated support manager',
      'Custom contract, compliance, and security review track',
    ],
  },
]

export const AI_SPEND_EXPLAINER = [
  'LLM and model usage is charged at provider cost without markup.',
  'Set spending caps so usage stays within your budget.',
  'Use your own provider credentials or studio-managed credentials where available.',
]
