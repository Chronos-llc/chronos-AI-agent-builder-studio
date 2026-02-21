import React, { useRef, useState } from 'react'
import { integrationConnectors } from '../../config/iconRegistry'
import { ProviderLogo } from '../brand/ProviderLogo'
import { Reveal } from '../Reveal'

export const IntegrationsShowcaseSection: React.FC = () => {
  const stripRef = useRef<HTMLDivElement | null>(null)
  const [dragging, setDragging] = useState(false)
  const [startX, setStartX] = useState(0)
  const [scrollLeft, setScrollLeft] = useState(0)
  const connectors = Object.values(integrationConnectors)

  const handleMouseDown = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!stripRef.current) return
    setDragging(true)
    setStartX(e.pageX - stripRef.current.offsetLeft)
    setScrollLeft(stripRef.current.scrollLeft)
  }

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!dragging || !stripRef.current) return
    e.preventDefault()
    const x = e.pageX - stripRef.current.offsetLeft
    const walk = (x - startX) * 1.2
    stripRef.current.scrollLeft = scrollLeft - walk
  }

  const endDrag = () => setDragging(false)

  return (
    <section id="integrations" className="bg-[#101824] py-16">
      <div className="mx-auto w-full max-w-7xl px-6">
        <Reveal>
          <h2 className="text-3xl font-semibold text-white">Integration Hub with install-ready connectors.</h2>
        </Reveal>
        <Reveal delay={80}>
          <p className="mt-3 max-w-3xl text-white/70">
            Add services, providers, and MCP servers from one marketplace. Drag to explore the catalog.
          </p>
        </Reveal>

        <Reveal delay={140}>
          <div
            ref={stripRef}
            className="mt-8 flex cursor-grab gap-3 overflow-x-auto rounded-2xl border border-white/10 bg-white/[0.03] p-4 active:cursor-grabbing"
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseLeave={endDrag}
            onMouseUp={endDrag}
          >
            {connectors.map(connector => (
              <div
                key={connector.id}
                className="min-w-[220px] rounded-xl border border-white/10 bg-black/20 px-3 py-3"
              >
                <div className="flex items-center gap-2">
                  <ProviderLogo name={connector.name} url={connector.url} size={30} />
                  <div className="text-sm font-medium text-white">{connector.name}</div>
                </div>
                <div className="mt-2 text-xs text-white/55">Connector in Integration Hub</div>
              </div>
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  )
}
