import React from 'react'
import { HeroSection } from '../components/landing/HeroSection'
import { AboutUsSection } from '../components/landing/AboutUsSection'
import { UnifiedStackSection } from '../components/landing/UnifiedStackSection'
import { HowChronosWorksSection } from '../components/landing/HowChronosWorksSection'
import { AgentSuiteDeepDiveSection } from '../components/landing/AgentSuiteDeepDiveSection'
import { AgenticThinkingSection } from '../components/landing/AgenticThinkingSection'
import { VoiceAndTelephonySection } from '../components/landing/VoiceAndTelephonySection'
import { CommunicationsSection } from '../components/landing/CommunicationsSection'
import { IntegrationsAndModelsSection } from '../components/landing/IntegrationsAndModelsSection'
import { PublishIntegrationSection } from '../components/landing/PublishIntegrationSection'
import { UseCasePlaceholdersSection } from '../components/landing/UseCasePlaceholdersSection'
import { CapabilityNarrativesSection } from '../components/landing/CapabilityNarrativesSection'
import { EnterpriseSection } from '../components/landing/EnterpriseSection'
import { ComprehensiveFooter } from '../components/landing/ComprehensiveFooter'

const LandingPage: React.FC = () => {
  return (
    <div className="landing-page min-h-screen text-white">
      <div className="landing-content">
        <HeroSection />
        <AboutUsSection />
        <UnifiedStackSection />
        <HowChronosWorksSection />
        <AgentSuiteDeepDiveSection />
        <AgenticThinkingSection />
        <VoiceAndTelephonySection />
        <CommunicationsSection />
        <IntegrationsAndModelsSection />
        <PublishIntegrationSection />
        <CapabilityNarrativesSection />
        <UseCasePlaceholdersSection />
        <EnterpriseSection />
        <ComprehensiveFooter />
      </div>
    </div>
  )
}

export default LandingPage
