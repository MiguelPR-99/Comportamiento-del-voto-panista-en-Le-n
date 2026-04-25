import fs from "node:fs";
import path from "node:path";
import { spawn, spawnSync } from "node:child_process";
import { setTimeout as wait } from "node:timers/promises";

const exportUrl = process.env.EXPORT_URL ?? "http://127.0.0.1:4173";
const outputPath = process.env.EXPORT_OUT ?? "exports/leon_pan_bivariate_desktop.png";
const selector = '[data-export-root="true"]';
const localBrowsersPath = path.resolve(".tmp/pw-browsers");
const localHostnames = new Set(["127.0.0.1", "localhost"]);

if (!process.env.PLAYWRIGHT_BROWSERS_PATH && fs.existsSync(localBrowsersPath)) {
  process.env.PLAYWRIGHT_BROWSERS_PATH = localBrowsersPath;
}

function parseHostname(url) {
  try {
    return new URL(url).hostname;
  } catch {
    return null;
  }
}

function parsePort(url) {
  try {
    const parsed = new URL(url);
    if (parsed.port) {
      return parsed.port;
    }
    return parsed.protocol === "https:" ? "443" : "80";
  } catch {
    return "4173";
  }
}

async function isServerReachable(url) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 2500);
  try {
    const response = await fetch(url, { method: "GET", signal: controller.signal });
    return response.ok;
  } catch {
    return false;
  } finally {
    clearTimeout(timeout);
  }
}

async function waitForServer(url, timeoutMs = 120000) {
  const startedAt = Date.now();
  while (Date.now() - startedAt < timeoutMs) {
    if (await isServerReachable(url)) {
      return true;
    }
    await wait(750);
  }
  return false;
}

function stopServer(serverProcess) {
  if (!serverProcess || !serverProcess.pid) {
    return;
  }
  if (process.platform === "win32") {
    spawnSync("taskkill", ["/pid", String(serverProcess.pid), "/T", "/F"], { stdio: "ignore" });
    return;
  }
  serverProcess.kill("SIGTERM");
}

async function ensureLocalServer(url) {
  const hostname = parseHostname(url);
  const port = parsePort(url);
  if (!hostname || !localHostnames.has(hostname)) {
    return null;
  }

  if (await isServerReachable(url)) {
    return null;
  }

  const serverProcess =
    process.platform === "win32"
      ? spawn(`npm run dev -- --hostname ${hostname} --port ${port}`, {
          stdio: "ignore",
          cwd: process.cwd(),
          env: process.env,
          shell: true
        })
      : spawn("npm", ["run", "dev", "--", "--hostname", hostname, "--port", port], {
          stdio: "ignore",
          cwd: process.cwd(),
          env: process.env
        });

  const ready = await waitForServer(url, 150000);
  if (!ready) {
    stopServer(serverProcess);
    throw new Error(`No se pudo iniciar servidor local para exportar en ${url}.`);
  }

  return serverProcess;
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
  const serverProcess = await ensureLocalServer(exportUrl);

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1600 } });
  page.on("console", (msg) => {
    if (msg.type() === "error") {
      console.error(`[browser-console] ${msg.text()}`);
    }
  });

  try {
    await page.goto(exportUrl, { waitUntil: "domcontentloaded", timeout: 120000 });
    await page.waitForSelector(selector, { timeout: 45000 });
    await page.waitForSelector(".legend-panel", { timeout: 45000 });
    await page.waitForFunction(() => document.querySelectorAll(".maplibregl-canvas").length >= 2, undefined, {
      timeout: 45000
    });
    await page.waitForFunction(() => {
      const button = document.querySelector(".export-png-button");
      return button ? button.textContent?.includes("Exportar PNG") : false;
    }, undefined, { timeout: 45000 });
    await page.waitForTimeout(550);
    const root = page.locator(selector);
    await root.screenshot({ path: outputPath, type: "png" });
    console.log(`PNG exportado en ${outputPath}`);
    if (serverProcess) {
      console.log("Servidor local temporal iniciado automaticamente para exportar.");
    }
  } finally {
    await browser.close();
    stopServer(serverProcess);
  }
}

run().catch((error) => {
  console.error(`Error al exportar PNG: ${error instanceof Error ? error.message : String(error)}`);
  process.exit(1);
});
