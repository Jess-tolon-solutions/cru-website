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
  { file: 'Main.dc.html',          out: 'ceilings-r-us-flyer-A-restaurants' },
  { file: 'PropertyFront.dc.html', out: 'ceilings-r-us-flyer-B-property-mgmt' },
  { file: 'OfferBack.dc.html',     out: 'ceilings-r-us-flyer-BACK-shared' },
];

// The artboards are authored at trim size with art running to the edge. A
// commercial printer needs that art carried 0.125" PAST the trim so a slight
// drift on the guillotine doesn't leave white slivers. Since the art isn't
// authored with a bleed margin, we scale it up just enough to cover the larger
// sheet and let the overflow be the bleed — a hair over 1.02x, invisible.
const TRIM = { w: 816, h: 1056, css: '8.5in 11in' };                  // 8.5 x 11
const BLEED = { w: 840, h: 1080, css: '8.75in 11.25in' };             // + 0.125" all round
const BLEED_SCALE = Math.max(BLEED.w / TRIM.w, BLEED.h / TRIM.h);

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

function buildPrintHtml({ head, markup }, bleed) {
  const page = bleed ? BLEED : TRIM;
  const wrapOpen = bleed ? '<div class="bleed-page"><div class="bleed-inner">' : '';
  const wrapClose = bleed ? '</div></div>' : '';
  const bleedCss = bleed ? `
  .bleed-page { width: ${BLEED.w}px; height: ${BLEED.h}px; overflow: hidden; position: relative; }
  .bleed-inner { position: absolute; top: 50%; left: 50%;
                 transform: translate(-50%, -50%) scale(${BLEED_SCALE.toFixed(5)});
                 transform-origin: center center; }` : '';
  return `<!doctype html>
<html>
<head>
<meta charset="utf-8">
${head}
<style>
  @page { size: ${page.css}; margin: 0; }
  html, body { margin: 0; padding: 0; background: #ffffff; }
  /* keep flood fills and dark panels — browsers drop backgrounds when printing */
  * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }${bleedCss}
</style>
</head>
<body>
${wrapOpen}${markup}${wrapClose}
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

const VARIANTS = [
  { bleed: true,  dir: 'for-printer-with-bleed', suffix: '-bleed' },
  { bleed: false, dir: 'no-bleed-office-printing', suffix: '' },
];

for (const v of VARIANTS) {
  const outDir = join(OUT, v.dir);
  mkdirSync(outDir, { recursive: true });
  console.log(`\n${v.dir}/`);

  for (const page of PAGES) {
    const src = readFileSync(resolve(HERE, page.file), 'utf8');
    const htmlPath = join(TMP, page.file.replace('.dc.html', v.suffix + '.print.html'));
    writeFileSync(htmlPath, buildPrintHtml(extractArtboard(src), v.bleed));

    const name = page.out + v.suffix + '.pdf';
    const pdfPath = join(outDir, name);
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
    console.log(`  ${name}  (${kb} KB)`);
  }
}

rmSync(TMP, { recursive: true, force: true });
console.log(`\nWrote ${PAGES.length * VARIANTS.length} PDFs to ${OUT}`);
console.log('  for-printer-with-bleed/    8.75 x 11.25in — trims to 8.5 x 11. Send these to a commercial printer.');
console.log('  no-bleed-office-printing/  8.5 x 11in exactly. For proofing or printing in-house.');
console.log('Text is vector in both; photos are embedded at print-assets/ resolution.');
