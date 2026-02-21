// @vitest-environment jsdom
import React from 'react'
import { act, cleanup, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import {
  DEFAULT_PLATFORM_LOADING_MESSAGES,
  PlatformLoadingScreen,
} from '../PlatformLoadingScreen'

describe('PlatformLoadingScreen', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    cleanup()
    vi.runOnlyPendingTimers()
    vi.useRealTimers()
  })

  it('rotates loading messages in order and loops', () => {
    render(<PlatformLoadingScreen stepIntervalMs={120} />)

    const status = screen.getByRole('status')
    expect(status.textContent).toBe(DEFAULT_PLATFORM_LOADING_MESSAGES[0])

    act(() => {
      vi.advanceTimersByTime(120)
    })
    expect(status.textContent).toBe(DEFAULT_PLATFORM_LOADING_MESSAGES[1])

    act(() => {
      vi.advanceTimersByTime(120 * (DEFAULT_PLATFORM_LOADING_MESSAGES.length - 1))
    })
    expect(status.textContent).toBe(DEFAULT_PLATFORM_LOADING_MESSAGES[0])
  })

  it('falls back to default messages when messages prop is empty', () => {
    render(<PlatformLoadingScreen messages={[]} />)
    expect(screen.getByRole('status').textContent).toBe(DEFAULT_PLATFORM_LOADING_MESSAGES[0])
  })

  it('renders full viewport overlay mode', () => {
    render(<PlatformLoadingScreen mode="overlay" />)

    const loader = screen.getByTestId('platform-loading-screen')
    expect(loader.getAttribute('data-loading-mode')).toBe('overlay')
    expect(loader.className).toContain('fixed')
    expect(loader.className).toContain('inset-0')
  })
})
