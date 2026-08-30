#!/usr/bin/env node
/**
 * Build print-ready PDFs from the .dc.html artboards.
 *
 *   node build-print-pdfs.mjs
 *
 * WHY THIS EXISTS
 * The design canvas's "Export PDF" rasterises each artboard at 96 px/inch.
 * That's fine for a screen proof and too soft for a commercial print run —
 * type especially, which comes out fuzzy rather than crisp.
 *
 * This renders the SAME artboard source through Chrome's print-to-PDF instead:
 *   - text and vector shapes stay vector, so they're sharp at any size
 *   - photos are embedded at the resolution of whatever is in print-assets/
 *
 * The artboards are authored at 816 x 1056 px, which is exactly 8.5 x 11 in
 * at CSS's fixed 96 px/inch — so the page size lines up with no scaling.
 *
 * Photos come from print-assets/ (full resolution) rather than the compressed
 * copies next to the artboards, which are sized to keep the canvas small.
 *
 * Output lands in pdf/ and is gitignored — regenerate rather than commit.
 */

import { readFileSync, writeFileSync, mkdirSync, existsSync, rmSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { dirname, resolve, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const ASSETS = resolve(HERE, 'print-assets');
const OUT = resolve(HERE, 'pdf');
const TMP = resolve(HERE, '.print-tmp');

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

const PAGES = [
  { file: 'Main.dc.html',          out: 'ceilings-r-us-flyer-A-restaurants.pdf' },
  { file: 'PropertyFront.dc.html', out: 'ceilings-r-us-flyer-B-property-mgmt.pdf' },
  { file: 'OfferBack.dc.html',     out: 'ceilings-r-us-flyer-BACK-shared.pdf' },
];

if (!existsSync(CHROME)) {
  console.error(`Chrome not found at:\n  ${CHROME}\nInstall Chrome or edit CHROME in this file.`);
  process.exit(1);
}
if (!existsSync(ASSETS)) {
  console.error(`Missing ${ASSETS} — the full-resolution photos live there.`);
  process.exit(1);
}

/** Pull the <helmet> styles and the artboard markup out of a .dc.html file. */
function extractArtboard(src) {
  const styles = [...src.matchAll(/<helmet>([\s\S]*?)<\/helmet>/g)]
    .map((m) => m[1])
    .join('\n');
  const body = src.match(/<\/helmet>([\s\S]*?)<\/x-dc>/);
  if (!body) throw new Error('could not find artboard markup between </helmet> and </x-dc>');
  return { head: styles.trim(), markup: body[1].trim() };
}

function buildPrintHtml({ head, markup }) {
  return `<!doctype html>
<html>
<head>
<meta charset="utf-8">
${head}
<style>
  @page { size: 8.5in 11in; margin: 0; }
  html, body { margin: 0; padding: 0; background: #ffffff; }
  /* keep flood fills and dark panels — browsers drop backgrounds when printing */
  * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
</style>
</head>
<body>
${markup}
</body>
</html>`;
}

rmSync(TMP, { recursive: true, force: true });
mkdirSync(TMP, { recursive: true });
mkdirSync(OUT, { recursive: true });

// Chrome resolves relative <img src> against the HTML file, so the staging dir
// holds the full-resolution photos under the same filenames the artboards use.
for (const name of ['hero-a.jpg', 'hero-b.jpg', 'before.jpg', 'after.jpg', 'prep.jpg', 'logo.png']) {
  const from = join(ASSETS, name);
  if (!existsSync(from)) throw new Error(`missing print asset: ${from}`);
  writeFileSync(join(TMP, name), readFileSync(from));
}

for (const page of PAGES) {
  const src = readFileSync(resolve(HERE, page.file), 'utf8');
  const htmlPath = join(TMP, page.file.replace('.dc.html', '.print.html'));
  writeFileSync(htmlPath, buildPrintHtml(extractArtboard(src)));

  const pdfPath = join(OUT, page.out);
  execFileSync(CHROME, [
    '--headless=new',
    '--disable-gpu',
    '--no-sandbox',
    '--no-pdf-header-footer',
    // give the webfonts time to arrive before the snapshot
    '--virtual-time-budget=15000',
    `--print-to-pdf=${pdfPath}`,
    `file://${htmlPath}`,
  ], { stdio: ['ignore', 'ignore', 'pipe'] });

  const kb = Math.round(readFileSync(pdfPath).length / 1024);
  console.log(`  ${page.out}  (${kb} KB)`);
}

rmSync(TMP, { recursive: true, force: true });
console.log(`\nWrote ${PAGES.length} PDFs to ${OUT}`);
console.log('Each is a single 8.5 x 11 page, full bleed. Text is vector; photos are embedded.');
