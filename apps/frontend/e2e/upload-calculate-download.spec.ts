import { test, expect } from "@playwright/test";

/**
 * CP-52: end-to-end test of the upload -> calculate -> download report
 * workflow.
 *
 * Every backend call is mocked via Playwright route interception. This is
 * deliberate: this test verifies the *frontend's own wiring* -- that
 * clicking "Extract", then "Calculate", then "Download" sends the right
 * requests in the right order and updates the UI correctly -- not the
 * backend's business logic, which already has its own dedicated pytest
 * suite (calculation engine, extraction, PDF report). Mocking means this
 * test runs deterministically without a live backend, Postgres, or a real
 * Gemini API key.
 */

const CANDIDATE_ACTIVITY_DATA = {
  facility: {
    organization_name: "Demo Steel Exporter",
    facility_name: "Izmir Steel Plant",
    country_code: "TR",
  },
  reporting_period: "2026-Q1",
  fuels: [
    {
      activity_name: "Natural gas reheating furnace",
      fuel_type: "natural_gas",
      amount: 1000.0,
      unit: "Nm3",
      emission_factor_kg_co2e_per_unit: 2.0,
      factor_source: "Test factor",
      input_reference: "invoice.pdf:p1",
      factor_quality: "national_default",
    },
  ],
  processes: [],
  electricity: [],
  purchased_inputs: [],
  transport: [],
};

test.describe("CP-52: upload -> calculate -> download report workflow", () => {
  test.beforeEach(async ({ page }) => {
    await page.route("**/v1/auth/token", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          access_token: "fake-e2e-token",
          token_type: "bearer",
          expires_in_seconds: 3600,
        }),
      })
    );

    await page.route("**/v1/documents/extract", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          source_filename: "invoice.pdf",
          candidate_activity_data: CANDIDATE_ACTIVITY_DATA,
        }),
      })
    );

    await page.route("**/v1/calculate", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          facility_name: "Izmir Steel Plant",
          reporting_period: "2026-Q1",
          scope_summaries: [],
          emission_lines: [],
          total_tco2e: 2.0,
          estimated_cbam_cost_eur: 160.0,
        }),
      })
    );

    await page.route("**/v1/reports/pdf", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/pdf",
        body: Buffer.from("%PDF-1.4 fake pdf content for e2e test"),
      })
    );
  });

  test("extracts a document, calculates emissions, and downloads the PDF report", async ({
    page,
  }) => {
    await page.goto("/");
    
    // Landing screen butonunu esnek regex ile bulup tıkla
    const enterButton = page.getByRole("button", { name: /panele git/i });
    if (await enterButton.isVisible()) {
      await enterButton.click();
    }

    await page.setInputFiles('input[aria-label="Document to extract"]', {
      name: "invoice.pdf",
      mimeType: "application/pdf",
      buffer: Buffer.from("fake pdf bytes"),
    });

    await page.getByRole("button", { name: "Extract candidate data" }).click();
    await expect(page.getByText(/Candidate data extracted from invoice\.pdf/)).toBeVisible();

    const calculateButton = page.getByRole("button", { name: "Calculate emissions" });
    await expect(calculateButton).toBeEnabled();
    await calculateButton.click();
    await expect(page.getByText(/Calculated 2 tCO2e/)).toBeVisible();

    const downloadButton = page.getByRole("button", { name: "Download PDF report" });
    await expect(downloadButton).toBeEnabled();

    const downloadPromise = page.waitForEvent("download");
    await downloadButton.click();
    const download = await downloadPromise;

    expect(download.suggestedFilename()).toBe("carbonpilot-cbam-report.pdf");
  });
});