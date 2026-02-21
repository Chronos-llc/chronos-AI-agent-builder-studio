import type { FullConfig } from '@playwright/test'
import { execFileSync } from 'node:child_process'
import fs from 'node:fs'
import path from 'node:path'

function parseSeedPayload(raw: string): Record<string, unknown> {
  const trimmed = raw.trim()
  if (!trimmed) {
    throw new Error('Seed script returned empty output')
  }

  try {
    return JSON.parse(trimmed) as Record<string, unknown>
  } catch {
    const firstBrace = trimmed.indexOf('{')
    const lastBrace = trimmed.lastIndexOf('}')
    if (firstBrace === -1 || lastBrace === -1 || lastBrace <= firstBrace) {
      throw new Error(`Unable to parse seed payload: ${trimmed}`)
    }
    return JSON.parse(trimmed.slice(firstBrace, lastBrace + 1)) as Record<string, unknown>
  }
}

function resolvePythonExecutable(backendDir: string): string {
  const candidates = [
    path.join(backendDir, '.venv', 'Scripts', 'python.exe'),
    path.join(backendDir, '.venv', 'bin', 'python'),
    'python',
  ]
  for (const candidate of candidates) {
    if (candidate === 'python' || fs.existsSync(candidate)) {
      return candidate
    }
  }
  return 'python'
}

async function globalSetup(_config: FullConfig) {
  const frontendDir = path.resolve(__dirname, '..')
  const repoRoot = path.resolve(frontendDir, '..')
  const backendDir = path.join(repoRoot, 'backend')
  const seedScript = path.join(backendDir, 'scripts', 'seed_e2e_marketplace_data.py')
  const outputPath = path.join(frontendDir, 'e2e', '.seed-data.json')
  const python = resolvePythonExecutable(backendDir)

  const stdout = execFileSync(python, [seedScript], {
    cwd: backendDir,
    encoding: 'utf-8',
    maxBuffer: 10 * 1024 * 1024,
    env: {
      ...process.env,
      PYTHONIOENCODING: 'utf-8',
      SQL_ECHO: process.env.SQL_ECHO || 'false',
      LOG_LEVEL: process.env.LOG_LEVEL || 'WARNING',
    },
  })

  const parsed = parseSeedPayload(stdout)
  fs.writeFileSync(outputPath, `${JSON.stringify(parsed, null, 2)}\n`, 'utf-8')
}

export default globalSetup
