import { defineConfig, devices } from '@playwright/test'
import fs from 'node:fs'
import path from 'node:path'
import { spawnSync } from 'node:child_process'

const repoRoot = path.resolve(__dirname, '..')
const backendRoot = path.join(repoRoot, 'backend')
const frontendRoot = path.join(repoRoot, 'frontend')

function commandExists(command: string, args: string[] = ['--version']): boolean {
  try {
    const result = spawnSync(command, args, { stdio: 'ignore', shell: true })
    return result.status === 0
  } catch {
    return false
  }
}

function resolveBackendPythonCommand(): string {
  const windowsVenv = path.join(backendRoot, '.venv', 'Scripts', 'python.exe')
  const posixVenv = path.join(backendRoot, '.venv', 'bin', 'python')
  if (fs.existsSync(windowsVenv)) {
    return `"${windowsVenv}" -m uvicorn app.main:app --host 127.0.0.1 --port 8000`
  }
  if (fs.existsSync(posixVenv)) {
    return `"${posixVenv}" -m uvicorn app.main:app --host 127.0.0.1 --port 8000`
  }
  return 'python -m uvicorn app.main:app --host 127.0.0.1 --port 8000'
}

function resolveMinioWebServer():
  | {
      command: string
      cwd: string
      url: string
      timeout: number
      reuseExistingServer: boolean
      env?: Record<string, string>
    }
  | null {
  if (commandExists('docker')) {
    return {
      command: 'docker compose up minio minio-init',
      cwd: repoRoot,
      url: 'http://127.0.0.1:9000',
      timeout: 180_000,
      reuseExistingServer: true,
    }
  }

  const configuredBin = process.env.MINIO_BIN?.trim()
  const candidateBins = [
    configuredBin,
    path.join(process.env.TEMP || '', 'minio.exe'),
    path.join(repoRoot, 'tools', 'minio', 'minio.exe'),
  ].filter((value): value is string => Boolean(value))
  const minioBin = candidateBins.find((candidate) => fs.existsSync(candidate))

  if (!minioBin && !commandExists('minio')) {
    return null
  }

  const executable = minioBin ? `"${minioBin}"` : 'minio'
  const minioDataDir = path.join(repoRoot, '.minio-data')
  fs.mkdirSync(minioDataDir, { recursive: true })
  return {
    command: `${executable} server "${minioDataDir}" --address 127.0.0.1:9000 --console-address 127.0.0.1:9001`,
    cwd: repoRoot,
    url: 'http://127.0.0.1:9000/minio/health/live',
    timeout: 180_000,
    reuseExistingServer: true,
    env: {
      MINIO_ROOT_USER: process.env.MINIO_ROOT_USER || 'minioadmin',
      MINIO_ROOT_PASSWORD: process.env.MINIO_ROOT_PASSWORD || 'minioadmin',
    },
  }
}

const minioWebServer = resolveMinioWebServer()
const skipWebServer = process.env.PLAYWRIGHT_SKIP_WEBSERVER === '1'
const skipGlobalSetup = process.env.PLAYWRIGHT_SKIP_GLOBAL_SETUP === '1'
const webServers = [
  ...(minioWebServer ? [minioWebServer] : []),
  {
    command: resolveBackendPythonCommand(),
    cwd: backendRoot,
    url: 'http://127.0.0.1:8000/docs',
    timeout: 180_000,
    reuseExistingServer: true,
  },
  {
    command: 'npm run dev -- --host 127.0.0.1 --port 3000',
    cwd: frontendRoot,
    url: 'http://127.0.0.1:3000',
    timeout: 180_000,
    reuseExistingServer: true,
  },
]

if (!minioWebServer) {
  console.warn(
    '[playwright] MinIO runtime was not auto-detected. Start MinIO manually on http://127.0.0.1:9000 before running e2e tests.',
  )
}

export default defineConfig({
  testDir: './e2e',
  tsconfig: './e2e/tsconfig.json',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 1 : undefined,
  timeout: 180_000,
  expect: {
    timeout: 15_000,
  },
  reporter: process.env.CI ? [['html', { open: 'never' }], ['list']] : [['list']],
  use: {
    baseURL: process.env.E2E_BASE_URL || 'http://127.0.0.1:3000',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  globalSetup: skipGlobalSetup ? undefined : './e2e/global-setup.ts',
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: skipWebServer ? undefined : webServers,
})
