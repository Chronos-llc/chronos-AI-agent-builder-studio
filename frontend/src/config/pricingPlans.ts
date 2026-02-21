export type PricingFeature = {
  id: string
  label: string
  description: string
}

export type PricingPlan = {
  id: 'payg' | 'lite' | 'lotus' | 'team' | 'special' | 'enterprise'
  name: string
  subtitle?: string
  priceLabel: string
  ctaLabel: string
  ctaHref: string
  accent: 'slate' | 'sky' | 'violet' | 'emerald' | 'rose' | 'neutral'
  badge?: string
  limitNote?: string
  features: PricingFeature[]
  note?: string
}

const FEATURES: Record<string, PricingFeature> = {
  monthly_credit: {
    id: 'monthly_credit',
    label: 'Free monthly AI credits',
    description: 'Included $5 monthly credit for AI usage to help you build and test before scaling your spend.',
  },
  one_agent_limit: {
    id: 'one_agent_limit',
    label: '1 bot/agent limit',
    description: 'Pay-as-you-go is restricted to one active agent at a time in your workspace.',
  },
  visual_builder: {
    id: 'visual_builder',
    label: 'Visual building studio',
    description: 'Build both voice and chat agents with visual controls, prompts, tools, and model pickers.',
  },
  community_support: {
    id: 'community_support',
    label: 'Community support',
    description: 'Access product guidance and troubleshooting through community channels and shared resources.',
  },
  human_handoff: {
    id: 'human_handoff',
    label: 'Human handoff',
    description: 'Route a live conversation from agent to human operator when escalation conditions are met.',
  },
  conversation_insights: {
    id: 'conversation_insights',
    label: 'Conversation insights',
    description: 'Analyze chat/call quality, user outcomes, and interaction trends from unified history.',
  },
  watermark_removal: {
    id: 'watermark_removal',
    label: 'Watermark removal',
    description: 'Remove default branding marks from embedded chat surfaces where applicable.',
  },
  proactive_chat_bubble: {
    id: 'proactive_chat_bubble',
    label: 'Proactive chat bubble',
    description: 'Trigger proactive engagement prompts on web experiences based on your rules.',
  },
  visual_kb_indexing: {
    id: 'visual_kb_indexing',
    label: 'Visual knowledge base indexing',
    description: 'Index uploaded documents and knowledge sources for retrieval-ready agent grounding.',
  },
  agentic_thinking: {
    id: 'agentic_thinking',
    label: 'Agentic Thinking (Beta)',
    description: 'Experimental internal dialogue mode where orchestrator agents create ephemeral sub-dialogue agents to plan before execution.',
  },
  live_chat_support: {
    id: 'live_chat_support',
    label: 'Technical support via live chat',
    description: 'Receive direct technical support from the Chronos team through live support channels.',
  },
  lotus_five_agents: {
    id: 'lotus_five_agents',
    label: 'Up to 5 agents',
    description: 'Lotus plan includes workspace limits for up to five active bots/agents.',
  },
  role_based_access: {
    id: 'role_based_access',
    label: 'Role-based access control',
    description: 'Assign workspace permissions by role to control editing, deployment, and operational actions.',
  },
  realtime_collaboration: {
    id: 'realtime_collaboration',
    label: 'Real-time collaboration',
    description: 'Enable teams to iterate on agents, settings, and workflows together in shared workspaces.',
  },
  custom_analytics: {
    id: 'custom_analytics',
    label: 'Custom analytics',
    description: 'Track custom operational metrics, performance indicators, and workflow outcomes.',
  },
  advanced_support: {
    id: 'advanced_support',
    label: 'Advanced support',
    description: 'Faster support response windows and deeper implementation guidance for teams.',
  },
  custom_development: {
    id: 'custom_development',
    label: 'Custom development',
    description: 'Chronos team delivers scoped custom features, flows, or integrations for your organization.',
  },
  ongoing_maintenance: {
    id: 'ongoing_maintenance',
    label: 'Ongoing maintenance',
    description: 'Continuous support for updates, optimization, and reliability hardening of your deployment.',
  },
  system_integration: {
    id: 'system_integration',
    label: 'System integration',
    description: 'Hands-on integration of Chronos with your internal systems, tools, and data environments.',
  },
  priority_support: {
    id: 'priority_support',
    label: 'Priority support',
    description: 'Highest-priority support queue for incidents and operational blockers.',
  },
  monthly_strategy_calls: {
    id: 'monthly_strategy_calls',
    label: 'Monthly strategy calls',
    description: 'Recurring planning sessions with the Chronos team to refine roadmap and outcomes.',
  },
  team_training_sessions: {
    id: 'team_training_sessions',
    label: 'Team training sessions',
    description: 'Structured onboarding and hands-on training for your builders and operators.',
  },
  whiteglove_onboarding: {
    id: 'whiteglove_onboarding',
    label: 'Whiteglove onboarding',
    description: 'Dedicated onboarding program with guided implementation, rollout planning, and adoption support.',
  },
  workspace_limits: {
    id: 'workspace_limits',
    label: 'Custom workspace limits',
    description: 'Tailored operational limits and quota controls aligned with enterprise governance.',
  },
  dedicated_manager: {
    id: 'dedicated_manager',
    label: 'Dedicated support manager',
    description: 'Named support lead coordinating execution, escalations, and lifecycle planning.',
  },
}

const PAYG_FEATURES: PricingFeature[] = [
  FEATURES.visual_builder,
  FEATURES.monthly_credit,
  FEATURES.community_support,
  FEATURES.one_agent_limit,
]

const LITE_PLUS_FEATURES: PricingFeature[] = [
  FEATURES.human_handoff,
  FEATURES.conversation_insights,
  FEATURES.watermark_removal,
  FEATURES.proactive_chat_bubble,
  FEATURES.visual_kb_indexing,
  FEATURES.agentic_thinking,
  FEATURES.live_chat_support,
]

const LOTUS_PLUS_FEATURES: PricingFeature[] = [
  FEATURES.agentic_thinking,
  FEATURES.live_chat_support,
  FEATURES.lotus_five_agents,
]

const TEAM_PLUS_FEATURES: PricingFeature[] = [
  FEATURES.role_based_access,
  FEATURES.realtime_collaboration,
  FEATURES.custom_analytics,
  FEATURES.advanced_support,
]

const SPECIAL_PLUS_FEATURES: PricingFeature[] = [
  FEATURES.custom_development,
  FEATURES.ongoing_maintenance,
  FEATURES.system_integration,
  FEATURES.priority_support,
  FEATURES.monthly_strategy_calls,
  FEATURES.team_training_sessions,
]

const ENTERPRISE_PLUS_FEATURES: PricingFeature[] = [
  FEATURES.whiteglove_onboarding,
  FEATURES.workspace_limits,
  FEATURES.dedicated_manager,
]

export const PRICING_PLANS: PricingPlan[] = [
  {
    id: 'payg',
    name: 'Pay-as-you-go',
    subtitle: 'Start for free',
    priceLabel: '$0 + AI Spend / mo (NGN 0)',
    ctaLabel: 'Start for free',
    ctaHref: '/app',
    accent: 'slate',
    limitNote: 'Restricted to 1 bot/agent',
    features: PAYG_FEATURES,
    note: 'AI Spend is billed separately at provider cost.',
  },
  {
    id: 'lite',
    name: 'Lite',
    priceLabel: '$85 + AI Spend / mo',
    ctaLabel: 'Get Lite',
    ctaHref: '/login',
    accent: 'sky',
    features: [...PAYG_FEATURES, ...LITE_PLUS_FEATURES],
  },
  {
    id: 'lotus',
    name: 'Lotus',
    subtitle: 'Power users',
    priceLabel: '$50 + AI Spend / mo',
    ctaLabel: 'Get Lotus',
    ctaHref: '/login',
    accent: 'violet',
    limitNote: 'Up to 5 bots/agents',
    features: [...PAYG_FEATURES, ...LOTUS_PLUS_FEATURES],
  },
  {
    id: 'team',
    name: 'Team & Developers',
    priceLabel: '$395 + AI Spend / mo',
    ctaLabel: 'Get Team Plan',
    ctaHref: '/login',
    accent: 'emerald',
    features: [...PAYG_FEATURES, ...LITE_PLUS_FEATURES, ...TEAM_PLUS_FEATURES],
  },
  {
    id: 'special',
    name: 'Special Service',
    subtitle: 'Managed by Chronos team',
    priceLabel: '$1,395 + AI Spend / mo',
    ctaLabel: 'Contact team',
    ctaHref: '/login',
    accent: 'rose',
    badge: 'Contact required',
    features: [...PAYG_FEATURES, ...LITE_PLUS_FEATURES, ...TEAM_PLUS_FEATURES, ...SPECIAL_PLUS_FEATURES],
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    priceLabel: 'Custom / Contact team',
    ctaLabel: 'Contact sales',
    ctaHref: '/login',
    accent: 'neutral',
    badge: 'Custom contract',
    features: [...PAYG_FEATURES, ...LITE_PLUS_FEATURES, ...TEAM_PLUS_FEATURES, ...ENTERPRISE_PLUS_FEATURES],
  },
]

export const AI_SPEND_EXPLAINER = [
  'LLM and model usage is billed directly at provider cost without markup.',
  'You can apply spend caps to keep monthly usage predictable.',
  'Use studio-provided credentials where available, or bring your own API keys.',
]
