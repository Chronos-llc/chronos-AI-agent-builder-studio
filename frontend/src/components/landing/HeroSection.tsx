import React from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import { ChronosLogo } from '../brand/ChronosLogo'
import { Reveal } from '../Reveal'
import { LanguageSwitcher } from './LanguageSwitcher'
import { LandingThemeToggle } from './LandingThemeToggle'
import { useMarketingI18n } from '../../hooks/useMarketingI18n'

export const HeroSection: React.FC = () => {
  const { t } = useMarketingI18n()

  return (
    <section className="landing-section relative overflow-hidden border-b border-white/10 pt-6">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_center,_rgba(45,212,191,0.16),_transparent_45%)]" />
      <div className="pointer-events-none absolute -left-20 top-16 h-72 w-72 rounded-full bg-cyan-400/15 blur-3xl" />
      <div className="pointer-events-none absolute -right-20 top-16 h-72 w-72 rounded-full bg-emerald-400/15 blur-3xl" />

      <header className="landing-container relative z-10 flex w-full items-center justify-between gap-4">
        <ChronosLogo textClassName="text-white" />
        <nav className="hidden items-center gap-6 text-sm text-white/70 md:flex">
          <a href="#unified-stack" className="hover:text-white">{t('nav.unifiedStack', 'Unified Stack')}</a>
          <a href="#suite" className="hover:text-white">{t('nav.agentSuite', 'Agent Suite')}</a>
          <a href="#channels" className="hover:text-white">{t('nav.channels', 'Channels')}</a>
          <Link to="/pricing" className="hover:text-white">{t('nav.pricing', 'Pricing')}</Link>
          <Link to="/docs" className="hover:text-white">{t('nav.docs', 'Docs')}</Link>
        </nav>
        <div className="flex items-center gap-2">
          <LanguageSwitcher />
          <LandingThemeToggle />
          <Link
            to="/login"
            className="rounded-full border border-white/20 px-4 py-2 text-sm text-white/80 transition hover:border-white/40 hover:text-white"
          >
            {t('nav.signin', 'Sign in')}
          </Link>
          <Link
            to="/app"
            className="rounded-full bg-white px-4 py-2 text-sm font-semibold text-[#081018] transition hover:bg-white/90"
          >
            {t('nav.launchStudio', 'Launch Studio')}
          </Link>
        </div>
      </header>

      <div className="landing-container relative z-10 pb-20 pt-12 md:pb-24 md:pt-16">
        <div className="mx-auto flex max-w-5xl flex-col items-center text-center">
          <Reveal>
            <ChronosLogo
              showWordmark={false}
              size={220}
              className="justify-center"
              markClassName="landing-hero-mark"
            />
          </Reveal>

          <Reveal delay={80}>
            <h1 className="mt-8 text-5xl font-bold leading-tight text-white md:text-7xl">
              <span>Chronos</span>
              <span className="bg-gradient-to-r from-cyan-400 to-sky-400 bg-clip-text text-transparent"> Studio</span>
            </h1>
          </Reveal>

          <Reveal delay={120}>
            <p className="landing-hero-tagline mt-7 max-w-4xl text-base font-medium text-cyan-200 md:text-2xl">
              {t('hero.title', 'Build agent systems that run real work every day.')}
            </p>
          </Reveal>

          <Reveal delay={160}>
            <p className="mt-7 max-w-4xl text-lg leading-relaxed text-white/75 md:text-[2rem] md:leading-[1.42]">
              {t(
                'hero.subtitle',
                'From Idea to Agent in Minutes. Build your own chatbot and give it tools to do actual work for you. Create a digital sidekick that works with your data, tools, voice, and workflows.'
              )}
            </p>
          </Reveal>

          <Reveal delay={220}>
            <div className="mt-10 flex flex-wrap items-center justify-center gap-3">
              <Link
                to="/app"
                className="inline-flex items-center gap-2 rounded-full bg-cyan-300 px-7 py-3 text-sm font-semibold text-[#081018] transition hover:bg-cyan-200"
              >
                {t('hero.start', 'Start building')}
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                to="/pricing"
                className="inline-flex items-center gap-2 rounded-full border border-cyan-200/40 bg-cyan-200/10 px-7 py-3 text-sm font-semibold text-cyan-100 transition hover:border-cyan-200 hover:bg-cyan-200/20"
              >
                {t('hero.compare', 'Compare plans')}
              </Link>
              <Link
                to="/docs"
                className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/5 px-7 py-3 text-sm font-semibold text-white transition hover:border-white/40 hover:bg-white/10"
              >
                {t('hero.readDocs', 'Read docs')}
              </Link>
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  )
}
