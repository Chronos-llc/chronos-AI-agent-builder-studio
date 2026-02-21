import React from 'react'
import { Link } from 'react-router-dom'
import { ChronosLogo } from '../components/brand/ChronosLogo'

const effectiveDate = 'February 19, 2026'

const sections = [
  {
    title: '1. Service Scope',
    body: 'Chronos Studio provides tools to build, configure, deploy, and operate AI agents, workflows, integrations, and communication-channel experiences. Access to specific capabilities may depend on your selected plan.',
  },
  {
    title: '2. Accounts and Security',
    body: 'You are responsible for the accuracy of account information, safeguarding credentials, and all activity under your account. Notify us promptly if you suspect unauthorized access.',
  },
  {
    title: '3. Acceptable Use',
    body: 'You agree not to use the platform for unlawful activity, abuse, exploitation, security testing without authorization, or content and actions that violate applicable law or third-party rights.',
  },
  {
    title: '4. Integrations and Third-Party Services',
    body: 'Chronos Studio can connect with external providers (for models, voice, messaging, telephony, and integrations). Your use of those providers remains subject to their own terms, policies, billing, and availability.',
  },
  {
    title: '5. Plans, Usage, and Billing Notes',
    body: 'Plan descriptions and usage expectations are provided for operational clarity. Final commercial terms, custom scopes, and enterprise commitments are governed by applicable order forms or negotiated agreements.',
  },
  {
    title: '6. Suspension and Termination',
    body: 'We may suspend or terminate access for security risk, abuse, breach of these terms, legal requirement, or non-payment where applicable. You may stop using the service at any time.',
  },
  {
    title: '7. Disclaimers and Limitation',
    body: 'The service is provided on an "as is" and "as available" basis. To the extent allowed by law, we do not guarantee uninterrupted or error-free operation. Liability is limited to the maximum extent permitted by applicable law.',
  },
  {
    title: '8. Updates to These Terms',
    body: 'We may revise these terms as the product and legal requirements evolve. Continued use after updates indicates acceptance of the revised terms.',
  },
  {
    title: '9. Contact and Complaints',
    body: 'For questions, reports, or complaints related to these terms, contact us using the details below.',
  },
] as const

const TermsPage: React.FC = () => {
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
          <h1 className="text-3xl font-semibold md:text-4xl">Terms of Service</h1>
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

export default TermsPage
