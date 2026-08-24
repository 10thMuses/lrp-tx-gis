// HTML -> PDF via headless Chromium, honouring the document's @page size.
// Fonts are embedded in the HTML as base64 @font-face, so output is stable.
import { chromium } from 'playwright';
const [, , src, out] = process.argv;
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const page = await browser.newPage();
await page.goto('file://' + src, { waitUntil: 'load' });
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(400);
await page.pdf({ path: out, preferCSSPageSize: true, printBackground: true });
await browser.close();
console.log('pdf ->', out);
