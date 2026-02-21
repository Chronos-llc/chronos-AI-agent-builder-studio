import React from 'react'
import { Link } from 'react-router-dom'
import { ChronosLogo } from '../brand/ChronosLogo'

const saasBadgeSnippet =
  '<a href="https://saasbrowser.com/en/saas/1189490/chronos-ai" target="_blank" rel="noopener"><img src="https://static-files.saasbrowser.com/saas-browser-badge-17.svg" alt="See our SaaS Browser listing" width="200" loading="lazy" fetchpriority="low"></a>'

export const ComprehensiveFooter: React.FC = () => {
  return (
    <footer className="border-t border-white/10 bg-[#050910]/80 py-12">
      <div className="landing-container grid gap-8 md:grid-cols-2 lg:grid-cols-5">
        <div className="lg:col-span-2">
          <ChronosLogo textClassName="text-white" markClassName="text-white" />
          <p className="mt-4 text-sm text-white/70">
            Chronos AI is a product line of Chronos Intelligence Systems by Mohex, focused on unified voice and chat agent
            operations, workflow orchestration, and production-grade automation.
          </p>
          <p className="mt-3 text-xs text-white/55">Founder and CEO: Jesse Newton Okoroma</p>
          <p className="mt-1 text-xs text-white/55">Address: 23 Ogbogoro Road, Port Harcourt, Rivers State, Nigeria.</p>
        </div>

        <div>
          <h4 className="text-sm font-semibold text-white">Platform</h4>
          <ul className="mt-3 space-y-2 text-sm text-white/65">
            <li>Agent Builder + Agent Suite</li>
            <li>Fuzzy assistant</li>
            <li>Workflow Generator + Virtual Computer</li>
            <li>Integrations Hub + MCP</li>
            <li>Voice Studio + Channels</li>
          </ul>
        </div>

        <div>
          <h4 className="text-sm font-semibold text-white">Product</h4>
          <ul className="mt-3 space-y-2 text-sm text-white/65">
            <li>
              <Link to="/pricing" className="hover:text-white">
                Pricing
              </Link>
            </li>
            <li>
              <Link to="/docs" className="hover:text-white">
                Docs
              </Link>
            </li>
            <li>
              <Link to="/login" className="hover:text-white">
                Login
              </Link>
            </li>
            <li>
              <a href="mailto:chronos.llc@mohex.org" className="hover:text-white">
                chronos.llc@mohex.org
              </a>
            </li>
          </ul>
        </div>

        <div>
          <h4 className="text-sm font-semibold text-white">Company</h4>
          <ul className="mt-3 space-y-2 text-sm text-white/65">
            <li>
              <a href="https://mohex.org/" target="_blank" rel="noopener noreferrer" className="hover:text-white">
                Mohex
              </a>
            </li>
            <li>
              <a href="https://mohex.org/#team" target="_blank" rel="noopener noreferrer" className="hover:text-white">
                Team
              </a>
            </li>
            <li>
              <Link to="/privacy" className="hover:text-white">
                Privacy Policy
              </Link>
            </li>
            <li>
              <Link to="/terms" className="hover:text-white">
                Terms of Service
              </Link>
            </li>
          </ul>
          <div className="mt-4" dangerouslySetInnerHTML={{ __html: saasBadgeSnippet }} />
        </div>
      </div>

      <div className="landing-container mt-8 flex items-center justify-between border-t border-white/10 pt-6 text-xs text-white/55">
        <span>{`(c) ${new Date().getFullYear()} Chronos AI. All rights reserved.`}</span>
        <span>Port Harcourt, Rivers State, Nigeria</span>
      </div>
    </footer>
  )
}
