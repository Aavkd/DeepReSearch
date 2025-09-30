import { test, expect } from '@playwright/test'

const BASE = process.env.E2E_BASE || 'http://localhost:3000'

test('can search and see sources', async ({ page }) => {
  await page.goto(BASE)
  await page.getByPlaceholder("Demandez n'importe quoi…").fill('latest Artemis mission')
  await page.getByRole('button', { name: 'Régénérer' }).click() // or main search button
  await page.waitForSelector('text=Sources')
  const items = await page.locator('a:text("http")').all()
  expect(items.length).toBeGreaterThan(0)
})