import React from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import type { PricingPlan } from '../../config/pricingPlans'
import { FeatureAccordionItem } from './FeatureAccordionItem'

interface PricingPlanCardProps {
  plan: PricingPlan
}

const accentMap: Record<PricingPlan['accent'], string> = {
  slate: 'border-white/15 bg-white/[0.03]',
  sky: 'border-sky-300/40 bg-sky-300/10',
  violet: 'border-violet-300/40 bg-violet-300/10',
  emerald: 'border-emerald-300/40 bg-emerald-300/10',
  rose: 'border-rose-300/40 bg-rose-300/10',
  neutral: 'border-white/25 bg-white/[0.05]',
}

export const PricingPlanCard: React.FC<PricingPlanCardProps> = ({ plan }) => {
  return (
    <article className={`rounded-3xl border p-6 ${accentMap[plan.accent]}`}>
      <div className="mb-5">
        <h3 className="text-2xl font-semibold text-white">{plan.name}</h3>
        {plan.subtitle && <p className="mt-1 text-sm text-white/65">{plan.subtitle}</p>}
        <p className="mt-4 text-3xl font-semibold text-white">{plan.priceLabel}</p>
        {plan.badge && (
          <span className="mt-3 inline-flex rounded-full border border-white/20 bg-black/20 px-2 py-1 text-[11px] uppercase tracking-[0.12em] text-white/65">
            {plan.badge}
          </span>
        )}
        {plan.limitNote && (
          <p className="mt-3 text-xs text-cyan-100/90">{plan.limitNote}</p>
        )}
      </div>

      <Link
        to={plan.ctaHref}
        className="mb-5 inline-flex items-center gap-2 rounded-full bg-white px-5 py-2.5 text-sm font-semibold text-[#070A10] transition hover:bg-white/90"
      >
        {plan.ctaLabel}
        <ArrowRight className="h-4 w-4" />
      </Link>

      <div className="space-y-2">
        {plan.features.map((feature, index) => (
          <FeatureAccordionItem
            key={`${plan.id}-${feature.id}`}
            feature={feature}
            defaultOpen={index === 0}
          />
        ))}
      </div>

      {plan.note && (
        <p className="mt-5 rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-xs text-white/65">
          {plan.note}
        </p>
      )}
    </article>
  )
}
