const puppeteer = require('puppeteer');
const http = require('http');
const fs = require('fs');
const path = require('path');

function createServer(directory, port) {
  return new Promise((resolve) => {
    const server = http.createServer((req, res) => {
      let filePath = path.join(directory, req.url === '/' ? 'free-ceiling-check/preview.html' : req.url);
      const ext = path.extname(filePath);
      const mimeTypes = {
        '.html': 'text/html',
        '.css': 'text/css',
        '.js': 'application/javascript',
        '.webp': 'image/webp',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.svg': 'image/svg+xml'
      };
      fs.readFile(filePath, (err, content) => {
        if (err) {
          res.writeHead(404);
          res.end('Not found');
        } else {
          res.writeHead(200, { 'Content-Type': mimeTypes[ext] || 'text/plain' });
          res.end(content);
        }
      });
    });
    server.listen(port, () => resolve(server));
  });
}

async function checkSEO() {
  const lighthouse = (await import('lighthouse')).default;
  const port = 8766;
  const server = await createServer(__dirname, port);
  const testUrl = `http://localhost:${port}/free-ceiling-check/preview.html`;

  const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox'] });

  try {
    const { lhr } = await lighthouse(testUrl, {
      port: new URL(browser.wsEndpoint()).port,
      output: 'json',
      onlyCategories: ['seo'],
      formFactor: 'mobile'
    });

    console.log('=== SEO AUDIT DETAILS ===\n');

    for (const ref of lhr.categories.seo.auditRefs) {
      const audit = lhr.audits[ref.id];
      if (audit && audit.score !== null && audit.score < 1) {
        console.log(`✗ ${audit.title} (score: ${audit.score})`);
        if (audit.description) {
          console.log(`  ${audit.description.split('[')[0].trim()}`);
        }
        console.log('');
      }
    }
  } finally {
    await browser.close();
    server.close();
  }
}

checkSEO().catch(console.error);
