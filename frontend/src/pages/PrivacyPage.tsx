import React from 'react'
import { Link } from 'react-router-dom'
import { ChronosLogo } from '../components/brand/ChronosLogo'

const effectiveDate = 'February 19, 2026'

const sections = [
  {
    title: '1. Data We Collect',
    body: 'We may collect account details, profile inputs, authentication/session data, usage and event logs, integration metadata, and configuration data needed to operate Chronos Studio.',
  },
  {
    title: '2. How We Use Data',
    body: 'We use data to provide authentication, maintain platform security, enable product features, personalize relevant experiences, support troubleshooting, and improve service quality.',
  },
  {
    title: '3. Third-Party Processing',
    body: 'When you enable external providers (for model inference, voice, channels, telephony, or integrations), limited data may be transmitted to those providers according to your configuration and their policies.',
  },
  {
    title: '4. Cookies, Local Storage, and Sessions',
    body: 'Chronos Studio uses browser storage and session tokens to maintain sign-in state, UI preferences, and secure access flows.',
  },
  {
    title: '5. Retention and Deletion',
    body: 'We retain data for operational and security needs, then delete or anonymize based on lifecycle rules and legal obligations. Account-deletion workflows may include delayed purge windows for safety and recovery.',
  },
  {
    title: '6. Security Practices',
    body: 'We apply reasonable technical and organizational safeguards to protect data in transit and at rest. No system is fully risk-free, and users should also protect their credentials and environments.',
  },
  {
    title: '7. Your Choices',
    body: 'You can update profile information, modify preferences, and request account-related support actions. Where available, deletion and data-rights requests are handled through support channels.',
  },
  {
    title: '8. Children',
    body: 'Chronos Studio is not intended for children under the age required by applicable law in your jurisdiction.',
  },
  {
    title: '9. Policy Updates',
    body: 'We may update this policy as product capabilities and legal obligations evolve. Material changes will be reflected with an updated effective date.',
  },
  {
    title: '10. Contact and Complaints',
    body: 'For privacy questions, complaints, or data-related requests, contact us using the details below.',
  },
] as const

const PrivacyPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#060b16] text-white">
      <div className="mx-auto w-full max-w-5xl px-6 py-10">
        <header className="mb-8 flex flex-wrap items-center justify-between gap-3">
          <ChronosLogo textClassName="text-white" />
          <div className="flex items-center gap-2 text-sm">
            <Link to="/" className="rounded-full border border-white/20 px-4 py-2 text-white/80 hover:border-white/40 hover:text-white">
              Home
            </Link>
            <Link to="/login" className="rounded-full border border-white/20 px-4 py-2 text-white/80 hover:border-white/40 hover:text-white">
              Sign in
            </Link>
          </div>
        </header>

        <main className="rounded-3xl border border-white/10 bg-white/[0.04] p-6 md:p-8">
          <h1 className="text-3xl font-semibold md:text-4xl">Privacy Policy</h1>
          <p className="mt-2 text-sm text-white/65">Effective date: {effectiveDate}</p>

          <div className="mt-8 space-y-6">
            {sections.map((section) => (
              <section key={section.title}>
                <h2 className="text-lg font-semibold text-white">{section.title}</h2>
                <p className="mt-2 text-sm leading-relaxed text-white/78">{section.body}</p>
              </section>
            ))}
          </div>

          <section className="mt-8 rounded-2xl border border-cyan-300/30 bg-cyan-300/10 p-5">
            <h2 className="text-base font-semibold text-cyan-100">Contact</h2>
            <p className="mt-2 text-sm text-cyan-50/90">
              Email: <a className="underline underline-offset-4" href="mailto:Chronos.llc@mohex.org">Chronos.llc@mohex.org</a>
            </p>
            <p className="mt-1 text-sm text-cyan-50/90">
              Website: <a className="underline underline-offset-4" href="https://mohex.org" target="_blank" rel="noopener noreferrer">https://mohex.org</a>
            </p>
          </section>
        </main>
      </div>
    </div>
  )
}

export default PrivacyPage
