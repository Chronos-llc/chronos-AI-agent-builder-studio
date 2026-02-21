import React, { useState } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'
import type { PricingFeature } from '../../config/pricingPlans'

interface FeatureAccordionItemProps {
  feature: PricingFeature
  defaultOpen?: boolean
}

export const FeatureAccordionItem: React.FC<FeatureAccordionItemProps> = ({
  feature,
  defaultOpen = false,
}) => {
  const [open, setOpen] = useState(defaultOpen)

  return (
    <div className="rounded-xl border border-white/10 bg-black/20">
      <button
        type="button"
        onClick={() => setOpen(prev => !prev)}
        className="flex w-full items-center justify-between gap-3 px-3 py-2 text-left"
      >
        <div className="flex items-center gap-2 text-sm text-white/90">
          <span className="text-cyan-300">?</span>
          <span>{feature.label}</span>
        </div>
        {open ? (
          <ChevronUp className="h-4 w-4 text-white/60" />
        ) : (
          <ChevronDown className="h-4 w-4 text-white/60" />
        )}
      </button>
      {open && (
        <div className="border-t border-white/10 px-3 py-2 text-xs text-white/70">
          {feature.description}
        </div>
      )}
    </div>
  )
}
