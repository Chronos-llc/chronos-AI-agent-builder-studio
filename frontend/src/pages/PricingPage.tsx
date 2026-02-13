import React from 'react'
import { Link } from 'react-router-dom'
import { ChronosLogo } from '../components/brand/ChronosLogo'
import { AI_SPEND_EXPLAINER, PRICING_PLANS } from '../config/pricingPlans'
import { PricingPlanCard } from '../components/pricing/PricingPlanCard'
import { ComprehensiveFooter } from '../components/landing/ComprehensiveFooter'
import { LanguageSwitcher } from '../components/landing/LanguageSwitcher'
import { useMarketingI18n } from '../hooks/useMarketingI18n'

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
      </div>
      <ComprehensiveFooter />
    </div>
  )
}

export default PricingPage
