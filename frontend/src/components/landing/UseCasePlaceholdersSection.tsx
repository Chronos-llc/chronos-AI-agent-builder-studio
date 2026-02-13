import React from 'react'
import { landingGallery } from '../../config/iconRegistry'
import { Reveal } from '../Reveal'

export const UseCasePlaceholdersSection: React.FC = () => {
  return (
    <section className="bg-[#0A1018] py-16">
      <div className="mx-auto w-full max-w-7xl px-6">
        <Reveal>
          <h2 className="text-3xl font-semibold text-white md:text-4xl">Use-case galleries and proof layouts</h2>
        </Reveal>
        <Reveal delay={80}>
          <p className="mt-4 max-w-3xl text-white/70">
            This section is intentionally designed for future use-case screenshots and outcome walk-throughs. Add your URLs later to
            show real examples of each Chronos capability in action.
          </p>
        </Reveal>

        <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {landingGallery.map((url, index) => (
            <Reveal key={url} delay={index * 70}>
              <article className="rounded-2xl border border-white/10 bg-white/[0.03] p-2 backdrop-blur">
                <img
                  src={url}
                  alt={`Use case placeholder ${index + 1}`}
                  loading="lazy"
                  className="h-60 w-full rounded-xl object-cover"
                />
                <div className="px-2 pb-2 pt-3 text-xs text-white/65">Replace with your use-case or feature walkthrough image URL.</div>
              </article>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  )
}
