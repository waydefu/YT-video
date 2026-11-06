#!/usr/bin/env node
// Capture the framed figure card (.iso-plate) of official Anatomy example pages at high resolution.
// Usage: node scripts/anatomy_capture.mjs <scale> <page.html> <out.png> [<page.html> <out.png> ...]
// Needs the `playwright` package and a Chromium it can launch (CI installs both). Layer-B asset step only:
// it renders upstream's own light-theme pages unchanged; nothing is edited or re-drawn.
import { createRequire } from 'node:module';
import path from 'node:path';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

const [, , scaleArg, ...pairs] = process.argv;
const scale = Number(scaleArg);
if (!scale || pairs.length < 2 || pairs.length % 2) {
  console.error('usage: anatomy_capture.mjs <scale> <page.html> <out.png> [...]');
  process.exit(2);
}
const browser = await chromium.launch({
  args: ['--no-sandbox', '--disable-dev-shm-usage', '--enable-webgl', '--use-gl=angle', '--use-angle=swiftshader'],
});
try {
  for (let i = 0; i < pairs.length; i += 2) {
    const [html, out] = [pairs[i], pairs[i + 1]];
    const page = await browser.newPage({ viewport: { width: 1000, height: 900 }, deviceScaleFactor: scale });
    await page.goto('file://' + path.resolve(html), { waitUntil: 'load', timeout: 60000 });
    await page.waitForTimeout(2500);
    const plate = page.locator('figure.iso-figure .iso-plate').first();
    await plate.screenshot({ path: out, timeout: 60000 });
    await page.close();
    console.log(JSON.stringify({ html: path.basename(html), out: path.basename(out) }));
  }
} finally {
  await browser.close();
}
