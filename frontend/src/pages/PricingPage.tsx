import React from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, CheckCircle2 } from 'lucide-react'
import { ChronosLogo } from '../components/brand/ChronosLogo'
import { AI_SPEND_EXPLAINER, PRICING_PLANS } from '../config/pricingPlans'
import { ComprehensiveFooter } from '../components/landing/ComprehensiveFooter'

const PricingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#070A10] text-white">
      <div className="mx-auto max-w-7xl px-6 py-8">
        <header className="mb-10 flex flex-wrap items-center justify-between gap-4">
          <ChronosLogo textClassName="text-white" markClassName="text-white" />
          <div className="flex items-center gap-3">
            <Link
              to="/"
              className="rounded-full border border-white/20 px-4 py-2 text-sm text-white/80 transition hover:border-white/40 hover:text-white"
            >
              Back to home
            </Link>
            <Link
              to="/app"
              className="rounded-full bg-white px-4 py-2 text-sm font-semibold text-[#070A10] transition hover:bg-white/90"
            >
              Open Studio
            </Link>
          </div>
        </header>

        <section className="mb-8">
          <p className="inline-flex rounded-full border border-cyan-300/30 bg-cyan-300/10 px-3 py-1 text-xs uppercase tracking-[0.2em] text-cyan-200">
            Usage-based pricing
          </p>
          <h1 className="mt-4 text-4xl font-semibold md:text-5xl">Choose the plan that matches your build velocity.</h1>
          <p className="mt-3 max-w-3xl text-white/70">
            All plans keep core Chronos Studio capabilities. Higher tiers expand orchestration depth, operational limits,
            support level, and managed services.
          </p>
        </section>

        <section className="mb-10 rounded-3xl border border-white/10 bg-white/[0.03] p-6">
          <h2 className="text-xl font-semibold">AI Spend Policy</h2>
          <div className="mt-4 grid gap-3 md:grid-cols-3">
            {AI_SPEND_EXPLAINER.map((line) => (
              <div key={line} className="rounded-2xl border border-white/10 bg-black/20 p-4 text-sm text-white/75">
                {line}
              </div>
            ))}
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-2">
          {PRICING_PLANS.map((plan) => (
            <article
              key={plan.id}
              className={`rounded-3xl border p-6 ${
                plan.highlight
                  ? 'border-cyan-300/50 bg-cyan-300/10 shadow-[0_0_40px_rgba(56,189,248,0.15)]'
                  : 'border-white/10 bg-white/[0.03]'
              }`}
            >
              <div className="mb-6">
                <h2 className="text-2xl font-semibold">{plan.name}</h2>
                {plan.subtitle && <p className="mt-1 text-sm text-white/65">{plan.subtitle}</p>}
                <p className="mt-5 text-3xl font-semibold">{plan.priceLabel}</p>
              </div>

              <Link
                to={plan.ctaHref}
                className="mb-6 inline-flex items-center gap-2 rounded-full bg-white px-5 py-2.5 text-sm font-semibold text-[#070A10] transition hover:bg-white/90"
              >
                {plan.ctaLabel}
                <ArrowRight className="h-4 w-4" />
              </Link>

              <div className="space-y-3">
                {plan.features.map((feature) => (
                  <div key={feature} className="flex items-start gap-3 text-sm text-white/80">
                    <CheckCircle2 className="mt-0.5 h-4 w-4 text-cyan-300" />
                    <span>{feature}</span>
                  </div>
                ))}
              </div>

              {plan.note && (
                <p className="mt-6 rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-xs text-white/70">
                  {plan.note}
                </p>
              )}
            </article>
          ))}
        </section>

        <section className="mt-12 rounded-3xl border border-white/10 bg-white/[0.03] p-6">
          <h3 className="text-lg font-semibold">Feature Access by Plan</h3>
          <div className="mt-4 overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead>
                <tr className="border-b border-white/10 text-white/60">
                  <th className="px-3 py-3">Capability</th>
                  <th className="px-3 py-3">Pay-as-you-go</th>
                  <th className="px-3 py-3">Lite</th>
                  <th className="px-3 py-3">Lotus</th>
                  <th className="px-3 py-3">Special</th>
                  <th className="px-3 py-3">Enterprise</th>
                </tr>
              </thead>
              <tbody className="text-white/80">
                {[
                  ['Agent Builder + Fuzzy', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes'],
                  ['Marketplace + Integrations Hub', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes'],
                  ['Voice Studio (advanced controls)', 'Basic', 'Advanced', 'Advanced', 'Advanced', 'Advanced'],
                  ['Workflow generator + code logs', 'Basic', 'Standard', 'Advanced', 'Advanced', 'Advanced'],
                  ['Virtual Computer controls', 'No', 'Yes', 'Yes', 'Yes', 'Yes'],
                  ['Support tier', 'Community', 'Priority live chat', 'Enhanced', 'Premium managed', 'Dedicated manager'],
                ].map((row) => (
                  <tr key={row[0]} className="border-b border-white/10 last:border-0">
                    {row.map((cell) => (
                      <td key={`${row[0]}-${cell}`} className="px-3 py-3">
                        {cell}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="mt-8 grid gap-4 lg:grid-cols-2">
          <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
            <h3 className="text-lg font-semibold">FAQ</h3>
            <div className="mt-4 space-y-3 text-sm text-white/75">
              <p><strong>How is AI Spend billed?</strong> Usage is charged at provider cost; plan fee is separate.</p>
              <p><strong>What does Free/Pro map to?</strong> Free maps to Pay-as-you-go; Pro maps to Lite.</p>
              <p><strong>Can I bring my own keys?</strong> Yes. You can use your own provider credentials.</p>
              <p><strong>Who gets Agentic Thinking and premium orchestration?</strong> Lotus, Special Service, and Enterprise tiers.</p>
            </div>
          </div>
          <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
            <h3 className="text-lg font-semibold">Contract Notes</h3>
            <div className="mt-4 space-y-3 text-sm text-white/75">
              <p>Special Service and Enterprise are custom agreements with scope, delivery, and support SLAs defined at contract stage.</p>
              <p>Telephony fees, model usage, and third-party API costs are billed separately from base subscription.</p>
              <p>Dedicated onboarding, security/compliance review, and workspace limits are configurable by plan.</p>
            </div>
          </div>
        </section>
      </div>
      <ComprehensiveFooter />
    </div>
  )
}

export default PricingPage
