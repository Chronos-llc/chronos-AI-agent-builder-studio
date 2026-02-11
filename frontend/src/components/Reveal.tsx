import React, { useEffect, useRef, useState } from 'react'
import { cn } from '../lib/utils'

type RevealDirection = 'up' | 'down' | 'left' | 'right'

interface RevealProps {
  children: React.ReactNode
  className?: string
  delay?: number
  once?: boolean
  direction?: RevealDirection
}

const directionMap: Record<RevealDirection, string> = {
  up: 'translate-y-6',
  down: '-translate-y-6',
  left: 'translate-x-6',
  right: '-translate-x-6',
}

export const Reveal: React.FC<RevealProps> = ({
  children,
  className,
  delay = 0,
  once = true,
  direction = 'up',
}) => {
  const ref = useRef<HTMLDivElement | null>(null)
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const node = ref.current
    if (!node) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
          if (once) observer.disconnect()
        } else if (!once) {
          setIsVisible(false)
        }
      },
      { threshold: 0.2 }
    )

    observer.observe(node)
    return () => observer.disconnect()
  }, [once])

  return (
    <div
      ref={ref}
      style={{ transitionDelay: `${delay}ms` }}
      className={cn(
        'transition-all duration-700 ease-out will-change-transform',
        isVisible ? 'opacity-100 translate-x-0 translate-y-0' : `opacity-0 ${directionMap[direction]}`,
        className
      )}
    >
      {children}
    </div>
  )
}

