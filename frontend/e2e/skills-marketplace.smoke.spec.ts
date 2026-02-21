import { expect, test, type Page } from '@playwright/test'
import fs from 'node:fs'
import path from 'node:path'

interface SeedUser {
  email: string
  password: string
  agent_id?: number
}

interface SeedData {
  admin: SeedUser
  user: SeedUser
}

const seedPath = path.resolve(__dirname, '.seed-data.json')
const fixturePath = path.resolve(__dirname, 'fixtures', 'sample-skill.md')

function loadSeedData(): SeedData {
  if (!fs.existsSync(seedPath)) {
    throw new Error(`Missing seed file at ${seedPath}. Run Playwright global setup first.`)
  }
  return JSON.parse(fs.readFileSync(seedPath, 'utf-8')) as SeedData
}

async function signIn(page: Page, email: string, password: string) {
  await page.goto('/login')
  await page.getByTestId('auth-method-email').click()
  const tos = page.getByTestId('auth-terms-checkbox')
  if (!(await tos.isChecked())) {
    await tos.check()
  }
  await page.getByTestId('auth-email-input').fill(email)
  await page.getByTestId('auth-password-input').fill(password)
  await page.getByTestId('auth-submit-button').click()
}

test.describe('Skills marketplace smoke flow', () => {
  test('upload -> review -> publish -> install', async ({ browser }) => {
    const seed = loadSeedData()
    const displayName = `E2E Skill ${Date.now()}`

    const userContext = await browser.newContext()
    const userPage = await userContext.newPage()
    await signIn(userPage, seed.user.email, seed.user.password)
    await userPage.waitForURL(/\/app(\/.*)?$/)

    expect(seed.user.agent_id).toBeTruthy()
    await userPage.goto(`/app/agents/${seed.user.agent_id}/edit`)
    await userPage.getByTestId('studio-tab-skills-marketplace').click()
    await expect(userPage.getByTestId('user-agent-skill-marketplace')).toBeVisible()

    await userPage.getByTestId('skill-upload-file-input').setInputFiles(fixturePath)
    await userPage.getByTestId('skill-upload-display-name-input').fill(displayName)
    await userPage.getByTestId('skill-upload-category-input').fill('automation')
    await userPage.getByTestId('skill-upload-description-input').fill(
      'E2E smoke submission for upload-review-publish-install validation.',
    )
    await userPage.getByTestId('skill-upload-submit').click()
    await expect(userPage.getByTestId('skill-upload-success')).toContainText('pending_review')

    const adminContext = await browser.newContext()
    const adminPage = await adminContext.newPage()
    await signIn(adminPage, seed.admin.email, seed.admin.password)
    await adminPage.waitForURL(/\/app\/admin(\/.*)?$/)
    await adminPage.goto('/app/admin/skills')
    await expect(adminPage.getByTestId('admin-skills-mode')).toBeVisible()
    await adminPage.getByTestId('admin-skills-tab-review').click()

    const reviewRow = adminPage
      .locator('[data-testid^="admin-review-row-"]')
      .filter({ hasText: displayName })
      .first()
    await expect(reviewRow).toBeVisible({ timeout: 20_000 })
    await reviewRow.getByRole('button', { name: 'Scan' }).click()
    await expect(adminPage.getByText('Scan completed')).toBeVisible()
    await reviewRow.getByRole('button', { name: 'Approve' }).click()
    await expect(adminPage.getByText('Submission approved')).toBeVisible()
    await reviewRow.getByRole('button', { name: 'Publish' }).click()
    await expect(adminPage.getByText('Submission published')).toBeVisible()

    await userPage.reload()
    await expect(userPage.getByTestId('user-agent-skill-marketplace')).toBeVisible()
    await userPage.getByTestId('user-skills-search-input').fill(displayName)

    const userCard = userPage.locator('[data-testid^="skill-card-"]').filter({ hasText: displayName }).first()
    await expect(userCard).toBeVisible({ timeout: 20_000 })
    await userCard.getByRole('button', { name: 'Open Skill' }).click()

    await userPage.getByTestId('skill-detail-install-button').click()
    await expect(userPage.getByTestId('skill-install-dialog')).toBeVisible()
    const agentInput = userPage.getByTestId('skill-install-agent-id-input')
    if ((await agentInput.inputValue()).trim().length === 0 && seed.user.agent_id) {
      await agentInput.fill(String(seed.user.agent_id))
    }
    await userPage.getByTestId('skill-install-confirm-button').click()
    await expect(userPage.getByText('Skill installed to agent knowledge base')).toBeVisible()

    await adminContext.close()
    await userContext.close()
  })
})

