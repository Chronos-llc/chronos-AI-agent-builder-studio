import React from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, Bot, Cable, MessagesSquare, Mic2, Sparkles, Workflow, BookOpen, Settings, Code, Clock, FileText, Rocket, Layout, Map, HelpCircle } from 'lucide-react'
import { ChronosLogo } from '../components/brand/ChronosLogo'
import { Reveal } from '../components/Reveal'
import { ComprehensiveFooter } from '../components/landing/ComprehensiveFooter'
import { LanguageSwitcher } from '../components/landing/LanguageSwitcher'
import { useMarketingI18n } from '../hooks/useMarketingI18n'
import { DOCUMENTATION_SECTIONS } from '../services/documentationService'

const DocsPage: React.FC = () => {
  const { t } = useMarketingI18n()

  // Get section icon
  const getSectionIcon = (sectionId: string) => {
    switch (sectionId) {
      case 'getting-started':
        return <Rocket className="h-5 w-5 text-cyan-200" />
      case 'platform':
        return <Layout className="h-5 w-5 text-cyan-200" />
      case 'agents':
        return <Bot className="h-5 w-5 text-cyan-200" />
      case 'voice-ai':
        return <Mic2 className="h-5 w-5 text-cyan-200" />
      case 'integrations':
        return <Cable className="h-5 w-5 text-cyan-200" />
      case 'api-reference':
        return <Code className="h-5 w-5 text-cyan-200" />
      case 'guides':
        return <Map className="h-5 w-5 text-cyan-200" />
      case 'resources':
        return <HelpCircle className="h-5 w-5 text-cyan-200" />
      default:
        return <BookOpen className="h-5 w-5 text-cyan-200" />
    }
  }

  return (
    <div className="min-h-screen bg-[#06080D] text-white">
      <div className="mx-auto w-full max-w-7xl px-6 py-8">
        <header className="mb-10 flex flex-wrap items-center justify-between gap-3">
          <ChronosLogo textClassName="text-white" markClassName="text-white" />
          <div className="flex items-center gap-3">
            <LanguageSwitcher />
            <Link to="/" className="rounded-full border border-white/20 px-4 py-2 text-sm text-white/80 hover:border-white/40 hover:text-white">
              {t('docs.home', 'Home')}
            </Link>
            <Link to="/pricing" className="rounded-full border border-white/20 px-4 py-2 text-sm text-white/80 hover:border-white/40 hover:text-white">
              {t('nav.pricing', 'Pricing')}
            </Link>
            <Link to="/app" className="rounded-full bg-white px-4 py-2 text-sm font-semibold text-[#070A10] hover:bg-white/90">
              {t('pricing.openStudio', 'Open Studio')}
            </Link>
          </div>
        </header>

        <Reveal>
          <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
            <p className="inline-flex rounded-full border border-cyan-300/30 bg-cyan-300/10 px-3 py-1 text-xs uppercase tracking-[0.2em] text-cyan-200">
              {t('docs.badge', 'Product docs')}
            </p>
            <h1 className="mt-4 text-4xl font-semibold md:text-5xl">{t('docs.title', 'Chronos Studio Docs Hub')}</h1>
            <p className="mt-3 max-w-3xl text-white/70">
              Understand how to build, run, and scale voice + chat agent systems in Chronos with unified orchestration.
            </p>
          </section>
        </Reveal>

        <section className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {DOCUMENTATION_SECTIONS.map((section, index) => (
            <Reveal key={section.id} delay={index * 70}>
              <Link 
                to={`/docs/${section.id}`} 
                className="group block rounded-2xl border border-white/10 bg-white/[0.03] p-5 hover:border-cyan-500/50 hover:bg-white/[0.05] transition-all"
              >
                <article id={section.id} className="h-full">
                  <div className="flex items-center gap-3 mb-3">
                    {getSectionIcon(section.id)}
                    <h2 className="text-lg font-semibold">{section.title}</h2>
                  </div>
                  <p className="text-sm text-white/75 mb-4">{section.description}</p>
                  <div className="flex items-center gap-2 text-sm text-cyan-300 group-hover:text-cyan-200">
                    Explore documentation
                    <ArrowRight className="h-4 w-4" />
                  </div>
                </article>
              </Link>
            </Reveal>
          ))}
        </section>

        <Reveal delay={140}>
          <section className="mt-8 rounded-3xl border border-amber-300/40 bg-amber-300/10 p-6">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <p className="inline-flex rounded-full border border-amber-200/60 px-2 py-1 text-[11px] uppercase tracking-[0.12em] text-amber-100">
                  Experimental
                </p>
                <h2 className="mt-3 text-2xl font-semibold">Agentic Thinking (Beta)</h2>
                <p className="mt-2 max-w-3xl text-sm text-amber-100/90">
                  Agentic Thinking introduces an internal reasoning phase where the orchestrator creates temporary dialogue-only sub-agents
                  to debate approaches, synthesize a plan, and then proceed to execution. These dialogue agents are ephemeral and removed
                  after completion.
                </p>
              </div>
              <Link to="/pricing" className="inline-flex items-center gap-2 rounded-full bg-white px-5 py-2.5 text-sm font-semibold text-[#070A10] hover:bg-white/90">
                View plan access
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </section>
        </Reveal>

        <Reveal delay={180}>
          <section className="mt-8 rounded-3xl border border-white/10 bg-white/[0.03] p-6">
            <h2 className="text-xl font-semibold">Plan Access Matrix (Summary)</h2>
            <div className="mt-4 overflow-x-auto">
              <table className="min-w-full text-left text-sm text-white/85">
                <thead>
                  <tr className="border-b border-white/10 text-white/60">
                    <th className="px-3 py-3">Capability</th>
                    <th className="px-3 py-3">Pay-as-you-go</th>
                    <th className="px-3 py-3">Lite</th>
                    <th className="px-3 py-3">Lotus</th>
                    <th className="px-3 py-3">Team</th>
                    <th className="px-3 py-3">Special</th>
                    <th className="px-3 py-3">Enterprise</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    ['Agent limits', '1', 'Standard', 'Up to 5', 'Higher', 'Higher', 'Custom'],
                    ['Agentic Thinking (Beta)', 'No', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes'],
                    ['Team controls', 'No', 'No', 'No', 'Yes', 'Yes', 'Yes'],
                    ['Managed services', 'No', 'No', 'No', 'No', 'Yes', 'Custom'],
                  ].map((row) => (
                    <tr key={row[0]} className="border-b border-white/10 last:border-0">
                      {row.map(cell => (
                        <td key={`${row[0]}-${cell}`} className="px-3 py-3">{cell}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </Reveal>

        <Reveal delay={220}>
          <section className="mt-8 rounded-3xl border border-white/10 bg-gradient-to-r from-cyan-300/10 to-sky-300/10 p-6">
            <h2 className="text-xl font-semibold">{t('docs.gettingStarted', 'Getting Started')}</h2>
            <p className="mt-2 max-w-3xl text-sm text-white/75">
              Start by creating your first agent, connecting model providers, and deploying to the Agent Suite for live operations.
            </p>
            <div className="mt-4 flex flex-wrap gap-3">
              <Link to="/app/agents/new" className="rounded-full bg-white px-5 py-2.5 text-sm font-semibold text-[#070A10] hover:bg-white/90">
                Build your first agent
              </Link>
              <Link to="/app/integrations" className="rounded-full border border-white/20 px-5 py-2.5 text-sm font-semibold text-white hover:border-white/40">
                Open Integrations Hub
              </Link>
            </div>
          </section>
        </Reveal>
      </div>
      <ComprehensiveFooter />
    </div>
  )
}

export default DocsPage
