import React from 'react'
import { HeroSection } from '../components/landing/HeroSection'
import { ModelAccessSection } from '../components/landing/ModelAccessSection'
import { FeatureInventorySection } from '../components/landing/FeatureInventorySection'
import { HowItWorksSection } from '../components/landing/HowItWorksSection'
import { IntegrationsShowcaseSection } from '../components/landing/IntegrationsShowcaseSection'
import { VoiceTelephonySection } from '../components/landing/VoiceTelephonySection'
import { GalleryCarouselSection } from '../components/landing/GalleryCarouselSection'
import { EnterpriseSection } from '../components/landing/EnterpriseSection'
import { ComprehensiveFooter } from '../components/landing/ComprehensiveFooter'

const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#070A10] text-white">
      <HeroSection />
      <ModelAccessSection />
      <FeatureInventorySection />
      <HowItWorksSection />
      <IntegrationsShowcaseSection />
      <VoiceTelephonySection />
      <GalleryCarouselSection />
      <EnterpriseSection />
      <ComprehensiveFooter />
    </div>
  )
}

export default LandingPage
