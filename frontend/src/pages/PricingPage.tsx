import React from 'react'
import { Link } from 'react-router-dom'
import { ChronosLogo } from '../components/brand/ChronosLogo'
import { AI_SPEND_EXPLAINER, PRICING_PLANS } from '../config/pricingPlans'
import { PricingPlanCard } from '../components/pricing/PricingPlanCard'
import { ComprehensiveFooter } from '../components/landing/ComprehensiveFooter'
import { LanguageSwitcher } from '../components/landing/LanguageSwitcher'
import { useMarketingI18n } from '../hooks/useMarketingI18n'

const ADDON_CARDS = [
  {
    id: 'file-storage',
    title: 'File Storage',
    description: 'Store documents, media, and workspace files.',
    included: [
      { plan: 'Pay-as-you-go', value: '100 MB' },
      { plan: 'Lite', value: '10 GB' },
      { plan: 'Lotus', value: '10 GB' },
      { plan: 'Team & Developers', value: '10 GB' },
    ],
    addonPrice: '$10/month for each additional 10 GB',
  },
  {
    id: 'vector-db',
    title: 'Vector DB Storage',
    description: 'Semantic memory storage used for retrieval and agent knowledge search.',
    included: [
      { plan: 'Pay-as-you-go', value: '100 MB' },
      { plan: 'Lite', value: '1 GB' },
      { plan: 'Lotus', value: '1 GB' },
      { plan: 'Team & Developers', value: '2 GB' },
    ],
    addonPrice: '$20/month for each additional 1 GB',
  },
  {
    id: 'agents',
    title: 'Agents',
    description: 'Number of agents you can run per workspace.',
    included: [
      { plan: 'Pay-as-you-go', value: '1' },
      { plan: 'Lite', value: '2' },
      { plan: 'Lotus', value: '5' },
      { plan: 'Team & Developers', value: '10' },
    ],
    addonPrice: '$10/month for each additional agent',
  },
  {
    id: 'table-rows',
    title: 'Table Rows',
    description: 'Rows for structured data in agent-owned tables.',
    included: [
      { plan: 'Pay-as-you-go', value: '1,000' },
      { plan: 'Lite', value: '100,000' },
      { plan: 'Lotus', value: '100,000' },
      { plan: 'Team & Developers', value: '200,000' },
    ],
    addonPrice: '$25/month for each additional 100,000 rows',
  },
  {
    id: 'collaborators',
    title: 'Collaborator Seats',
    description: 'Members in a user workspace (including operational contributors).',
    included: [
      { plan: 'Pay-as-you-go', value: '1 seat' },
      { plan: 'Lite', value: '2 seats' },
      { plan: 'Lotus', value: '1 seat' },
      { plan: 'Team & Developers', value: '5 seats' },
    ],
    addonPrice: '$25/month for each additional seat',
  },
]

const PRICING_FAQ = [
  {
    q: 'How are add-ons applied to my workspace limits?',
    a: 'Add-ons increase your base plan limits immediately after admin allocation. Usage snapshots include both base and add-on allocations in real time.',
  },
  {
    q: 'Are AI spend limits hard caps?',
    a: 'Yes for capped plans (Pay-as-you-go, Lite, Lotus, Team, Special Service). Enterprise defaults to custom/no hard cap unless specified in your contract.',
  },
  {
    q: 'Can I buy add-ons in advance for a future billing cycle?',
    a: 'Yes. Add-on allocations support effective dates, so operations can schedule activation and expiration windows.',
  },
  {
    q: 'Do overages auto-purchase add-ons?',
    a: 'Not in this phase. Overage estimates are calculated, and add-ons are applied by admin action.',
  },
  {
    q: 'How do collaborator seats get counted?',
    a: 'Seats are counted as workspace owner + active members. Removing a member frees a seat for future assignments.',
  },
  {
    q: 'How is vector DB storage measured?',
    a: 'Vector storage is computed from indexed chunk content footprint used by retrieval pipelines.',
  },
  {
    q: 'How is file storage measured?',
    a: 'File storage uses uploaded object size (or legacy file size fallback) across your agents.',
  },
  {
    q: 'What happens when I reach an agent limit?',
    a: 'Agent creation requests are blocked until seats are freed or add-on agent units are assigned.',
  },
  {
    q: 'What happens when I hit table-row limits?',
    a: 'New table-row writes are restricted once your limit is reached, unless capacity is expanded with add-ons.',
  },
  {
    q: 'Do balances support multiple currencies?',
    a: 'Yes. Balances are per-currency ledgers. Credits and debits are not auto-converted between currencies.',
  },
  {
    q: 'Can admins adjust user balances?',
    a: 'Yes. Admins can credit or debit balances per currency with reason tracking and transaction history.',
  },
  {
    q: 'Is object storage included in usage tracking?',
    a: 'Yes. Uploaded file objects are tracked through storage metadata so limits and usage remain consistent.',
  },
]

const PricingPage: React.FC = () => {
  const { t } = useMarketingI18n()

  return (
    <div className="min-h-screen bg-[#06080D] text-white">
      <div className="mx-auto max-w-7xl px-6 py-8">
        <header className="mb-10 flex flex-wrap items-center justify-between gap-4">
          <ChronosLogo textClassName="text-white" markClassName="text-white" />
          <div className="flex items-center gap-3">
            <LanguageSwitcher />
            <Link
              to="/"
              className="rounded-full border border-white/20 px-4 py-2 text-sm text-white/80 transition hover:border-white/40 hover:text-white"
            >
              {t('pricing.backHome', 'Back to home')}
            </Link>
            <Link
              to="/docs"
              className="rounded-full border border-white/20 px-4 py-2 text-sm text-white/80 transition hover:border-white/40 hover:text-white"
            >
              {t('nav.docs', 'Docs')}
            </Link>
            <Link
              to="/app"
              className="rounded-full bg-white px-4 py-2 text-sm font-semibold text-[#070A10] transition hover:bg-white/90"
            >
              {t('pricing.openStudio', 'Open Studio')}
            </Link>
          </div>
        </header>

        <section className="mb-10">
          <p className="inline-flex rounded-full border border-cyan-300/30 bg-cyan-300/10 px-3 py-1 text-xs uppercase tracking-[0.2em] text-cyan-200">
            {t('pricing.usageBadge', 'Usage-based pricing')}
          </p>
          <h1 className="mt-4 max-w-4xl text-4xl font-semibold leading-tight md:text-5xl">
            {t('pricing.title', 'Choose the plan that matches how you build and operate agents.')}
          </h1>
          <p className="mt-4 max-w-3xl text-white/70">
            Chronos combines voice, chat, workflows, tool orchestration, and agent suite operations in one stack. Plan tiers
            expand limits, support depth, and team capabilities.
          </p>
        </section>

        <section className="mb-10 rounded-3xl border border-white/10 bg-white/[0.03] p-6">
          <h2 className="text-xl font-semibold text-white">{t('pricing.aiSpendPolicy', 'AI Spend Policy')}</h2>
          <div className="mt-4 grid gap-3 md:grid-cols-3">
            {AI_SPEND_EXPLAINER.map((line) => (
              <div key={line} className="rounded-2xl border border-white/10 bg-black/20 p-4 text-sm text-white/75">
                {line}
              </div>
            ))}
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-2">
          {PRICING_PLANS.map(plan => (
            <PricingPlanCard key={plan.id} plan={plan} />
          ))}
        </section>

        <section className="mt-12">
          <div className="mb-6">
            <p className="inline-flex rounded-full border border-emerald-300/30 bg-emerald-300/10 px-3 py-1 text-xs uppercase tracking-[0.2em] text-emerald-200">
              Add-ons
            </p>
            <h2 className="mt-4 text-3xl font-semibold md:text-4xl">Extend your plan capacity</h2>
            <p className="mt-3 max-w-3xl text-white/70">
              Add-ons expand core platform resources and are reflected immediately in usage meters.
            </p>
          </div>
          <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
            {ADDON_CARDS.map((card) => (
              <article key={card.id} className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
                <h3 className="text-xl font-semibold">{card.title}</h3>
                <p className="mt-2 text-sm text-white/70">{card.description}</p>
                <div className="mt-4 space-y-2 text-sm text-white/80">
                  {card.included.map((entry) => (
                    <div key={`${card.id}-${entry.plan}`} className="flex items-center justify-between gap-3 rounded-lg bg-black/20 px-3 py-2">
                      <span>{entry.plan}</span>
                      <span className="font-medium">{entry.value}</span>
                    </div>
                  ))}
                </div>
                <p className="mt-4 text-sm font-medium text-cyan-200">{card.addonPrice}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="mt-10 grid gap-6 lg:grid-cols-2">
          <article className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
            <h3 className="text-lg font-semibold">Plan Notes</h3>
            <div className="mt-4 space-y-3 text-sm text-white/75">
              <p>
                <strong>Pay-as-you-go:</strong> capped at one bot/agent, with included monthly AI spend credit.
              </p>
              <p>
                <strong>Lotus:</strong> power-user plan with up to five agents and advanced creation flexibility.
              </p>
              <p>
                <strong>Special Service & Enterprise:</strong> include direct engagement with Chronos team and custom delivery tracks.
              </p>
            </div>
          </article>

          <article className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
            <h3 className="text-lg font-semibold">Contracts & Billing</h3>
            <div className="mt-4 space-y-3 text-sm text-white/75">
              <p>Base subscription and AI spend are separate line items.</p>
              <p>Telephony, provider APIs, and third-party services are billed based on usage and provider terms.</p>
              <p>Special Service and Enterprise include scoped agreements, support coverage, and implementation terms.</p>
            </div>
          </article>
        </section>

        <section className="mt-12 rounded-3xl border border-white/10 bg-white/[0.03] p-6 md:p-8">
          <h2 className="text-3xl font-semibold">Pricing FAQ</h2>
          <p className="mt-3 max-w-3xl text-white/70">
            Detailed answers on plans, limits, metering, add-ons, and billing operations.
          </p>
          <div className="mt-6 space-y-3">
            {PRICING_FAQ.map((item) => (
              <details key={item.q} className="group rounded-2xl border border-white/10 bg-black/20 p-4">
                <summary className="cursor-pointer list-none pr-6 text-base font-semibold text-white">
                  {item.q}
                </summary>
                <p className="mt-3 text-sm leading-relaxed text-white/75">{item.a}</p>
              </details>
            ))}
          </div>
          <div className="mt-8 rounded-2xl border border-cyan-400/30 bg-cyan-400/10 p-4 text-sm">
            <span className="font-semibold text-white">Still have questions? </span>
            <a
              href="mailto:Chronos.llc@mohex.org"
              className="font-medium text-cyan-200 underline decoration-cyan-300/70 underline-offset-4 hover:text-cyan-100"
            >
              Get in touch
            </a>
            <span className="text-white/80"> at Chronos.llc@mohex.org</span>
          </div>
        </section>
      </div>
      <ComprehensiveFooter />
    </div>
  )
}

export default PricingPage
