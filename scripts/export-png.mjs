import fs from "node:fs";
import path from "node:path";

const exportUrl = process.env.EXPORT_URL ?? "http://127.0.0.1:3000";
const outputPath = process.env.EXPORT_OUT ?? "exports/leon_pan_bivariate_desktop.png";
const selector = '[data-export-root="true"]';
const localBrowsersPath = path.resolve(".tmp/pw-browsers");

if (!process.env.PLAYWRIGHT_BROWSERS_PATH && fs.existsSync(localBrowsersPath)) {
  process.env.PLAYWRIGHT_BROWSERS_PATH = localBrowsersPath;
}

async function run() {
  let chromium;
  try {
    ({ chromium } = await import("playwright"));
  } catch {
    console.error("Falta la dependencia playwright. Instala con: npm install --save-dev playwright");
    process.exit(1);
  }

  fs.mkdirSync(path.dirname(outputPath), { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1600 } });

  try {
    await page.goto(exportUrl, { waitUntil: "networkidle", timeout: 120000 });
    await page.waitForSelector(selector, { timeout: 45000 });
    const root = page.locator(selector);
    await root.screenshot({ path: outputPath, type: "png" });
    console.log(`PNG exportado en ${outputPath}`);
    console.log("Nota: este comando requiere la app corriendo en http://127.0.0.1:3000.");
  } finally {
    await browser.close();
  }
}

run().catch((error) => {
  console.error(`Error al exportar PNG: ${error instanceof Error ? error.message : String(error)}`);
  process.exit(1);
});
