/*
Copyright (c) 2026 NyxeraLabs
Author: José María Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0

You may:
Study
Modify
Use for internal security testing

You may NOT:
Offer as a commercial service
Sell derived competing products
*/

import { expect, test } from "@playwright/test";

test("registration remains gated until all policies are accepted", async ({ page }) => {
  await page.goto("/ui/login");
  await expect(page.getByRole("heading", { name: "Operator Access" })).toBeVisible();

  await page.getByRole("button", { name: "Register" }).click();
  const continueButton = page.getByRole("button", { name: "Continue to Registration" });
  await expect(continueButton).toBeDisabled();

  const checkboxes = page.getByRole("checkbox");
  await expect(checkboxes).toHaveCount(3);
  await checkboxes.nth(0).check();
  await checkboxes.nth(1).check();
  await checkboxes.nth(2).check();

  await expect(continueButton).toBeEnabled();
  await continueButton.click();
  await expect(page.getByRole("button", { name: "Register User" })).toBeVisible();
});

