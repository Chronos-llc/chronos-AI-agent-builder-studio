import React, { useRef } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { landingGallery } from '../../config/iconRegistry'
import { Reveal } from '../Reveal'

export const GalleryCarouselSection: React.FC = () => {
  const ref = useRef<HTMLDivElement | null>(null)

  const scrollByAmount = (amount: number) => {
    if (!ref.current) return
    ref.current.scrollBy({ left: amount, behavior: 'smooth' })
  }

  return (
    <section className="bg-[#0E141D] py-16">
      <div className="mx-auto w-full max-w-7xl px-6">
        <Reveal>
          <h2 className="text-3xl font-semibold text-white">Platform snapshots</h2>
        </Reveal>
        <Reveal delay={80}>
          <p className="mt-3 text-white/70">
            Explore visual previews of studio experiences in a glass-style carousel.
          </p>
        </Reveal>

        <Reveal delay={140}>
          <div className="mt-6 flex items-center justify-end gap-2">
            <button
              type="button"
              onClick={() => scrollByAmount(-420)}
              className="rounded-full border border-white/20 bg-white/5 p-2 text-white/80 hover:border-white/40"
              aria-label="Scroll left"
            >
              <ChevronLeft className="h-5 w-5" />
            </button>
            <button
              type="button"
              onClick={() => scrollByAmount(420)}
              className="rounded-full border border-white/20 bg-white/5 p-2 text-white/80 hover:border-white/40"
              aria-label="Scroll right"
            >
              <ChevronRight className="h-5 w-5" />
            </button>
          </div>
        </Reveal>

        <div
          ref={ref}
          className="mt-4 flex snap-x snap-mandatory gap-4 overflow-x-auto pb-2"
        >
          {landingGallery.map((url, idx) => (
            <div
              key={url}
              className="group min-w-[280px] max-w-[420px] flex-1 snap-start rounded-3xl border border-white/15 bg-white/[0.04] p-2 backdrop-blur md:min-w-[360px]"
            >
              <img
                src={url}
                alt={`Chronos preview ${idx + 1}`}
                loading="lazy"
                className="h-[420px] w-full rounded-2xl object-cover transition duration-300 group-hover:scale-[1.01]"
              />
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
