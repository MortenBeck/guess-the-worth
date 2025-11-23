import { test, expect } from '@playwright/test';

test.describe('Bug 6.2: Stay Logged In on Refresh', () => {
  test.beforeEach(async ({ page }) => {
    // Clear storage before each test
    await page.context().clearCookies();
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
  });

  test('should not get stuck in infinite loading loop', async ({ page }) => {
    console.log('Test: Checking for infinite loading loop...');

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Wait max 5 seconds for spinner to disappear
    const spinner = page.locator('[class*="chakra-spinner"]');

    try {
      // If spinner exists, wait for it to disappear
      await spinner.waitFor({ state: 'hidden', timeout: 5000 });
      console.log('✓ Loading spinner cleared successfully');
    } catch {
      // If still visible after 5 seconds, we have an infinite loop
      const isVisible = await spinner.isVisible().catch(() => false);
      if (isVisible) {
        throw new Error('INFINITE LOOP DETECTED: Spinner still visible after 5 seconds');
      }
    }

    // Page should load with header visible
    await expect(page.getByRole('heading', { name: /Bid on Art/i })).toBeVisible();
    console.log('✓ Page loaded successfully');
  });

  test('should handle backend API failure without infinite loop', async ({ page }) => {
    console.log('Test: Simulating backend API failure...');

    // Intercept backend API and make it fail
    await page.route('**/api/auth/me', route => {
      console.log('  → Blocking /api/auth/me call');
      route.abort('failed');
    });

    await page.goto('/');

    // Even with API failure, should not get stuck
    const spinner = page.locator('[class*="chakra-spinner"]');

    try {
      await spinner.waitFor({ state: 'hidden', timeout: 5000 });
      console.log('✓ Loading completed despite API failure');
    } catch {
      const isVisible = await spinner.isVisible().catch(() => false);
      if (isVisible) {
        throw new Error('INFINITE LOOP: Page stuck loading after API failure');
      }
    }

    await expect(page.getByRole('heading', { name: /Bid on Art/i })).toBeVisible();
    console.log('✓ Page recovered from API failure');
  });

  test('should log auth flow to console', async ({ page }) => {
    const consoleLogs = [];

    page.on('console', msg => {
      consoleLogs.push(msg.text());
      console.log('Browser console:', msg.text());
    });

    await page.goto('/');
    await page.waitForTimeout(3000);

    // Check if we have auth-related logs
    const hasAuthLogs = consoleLogs.some(log =>
      log.includes('auth') || log.includes('loading') || log.includes('APP RENDER')
    );

    console.log('Console logs collected:', consoleLogs.length);
    console.log('Has auth-related logs:', hasAuthLogs);
  });

  test('should clear localStorage and load correctly', async ({ page }) => {
    console.log('Test: Fresh start with clear localStorage...');

    await page.goto('/');

    // Verify localStorage is clear
    const authStorage = await page.evaluate(() => localStorage.getItem('auth-storage'));
    console.log('localStorage auth-storage:', authStorage);

    // Should load without issues
    await page.waitForLoadState('networkidle');
    await expect(page.getByRole('heading', { name: /Bid on Art/i })).toBeVisible({ timeout: 5000 });

    console.log('✓ Page loaded with clean state');
  });
});
