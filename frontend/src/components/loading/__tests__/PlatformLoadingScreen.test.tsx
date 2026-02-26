// @vitest-environment jsdom
import React from 'react'
import { act, cleanup, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import {
  DEFAULT_PLATFORM_LOADING_MESSAGES,
  PlatformLoadingScreen,
} from '../PlatformLoadingScreen'
import { ThemeProvider } from '../../../contexts/ThemeContext'

const renderWithTheme = (node: React.ReactElement) =>
  render(
    <ThemeProvider>
      {node}
    </ThemeProvider>,
  )

describe('PlatformLoadingScreen', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: vi.fn().mockImplementation((query: string) => ({
        matches: query.includes('dark'),
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    })
  })

  afterEach(() => {
    cleanup()
    vi.runOnlyPendingTimers()
    vi.useRealTimers()
  })

  it('rotates loading messages in order and loops', () => {
    renderWithTheme(<PlatformLoadingScreen stepIntervalMs={120} />)

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
    renderWithTheme(<PlatformLoadingScreen messages={[]} />)
    expect(screen.getByRole('status').textContent).toBe(DEFAULT_PLATFORM_LOADING_MESSAGES[0])
  })

  it('renders full viewport overlay mode', () => {
    renderWithTheme(<PlatformLoadingScreen mode="overlay" />)

    const loader = screen.getByTestId('platform-loading-screen')
    expect(loader.getAttribute('data-loading-mode')).toBe('overlay')
    expect(loader.className).toContain('fixed')
    expect(loader.className).toContain('inset-0')
  })
})
