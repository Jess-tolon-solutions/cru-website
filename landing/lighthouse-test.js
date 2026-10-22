const puppeteer = require('puppeteer');
const path = require('path');
const http = require('http');
const fs = require('fs');

// Simple static file server
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

    server.listen(port, () => {
      resolve(server);
    });
  });
}

async function runLighthouse() {
  const lighthouse = (await import('lighthouse')).default;

  // Start local server
  const port = 8765;
  const server = await createServer(__dirname, port);
  const testUrl = `http://localhost:${port}/free-ceiling-check/preview.html`;

  console.log('Testing:', testUrl);
  console.log('Running Lighthouse mobile audit...\n');

  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-gpu']
  });

  try {
    const { lhr } = await lighthouse(testUrl, {
      port: new URL(browser.wsEndpoint()).port,
      output: 'json',
      onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'],
      formFactor: 'mobile',
      screenEmulation: {
        mobile: true,
        width: 390,
        height: 844,
        deviceScaleFactor: 2,
        disabled: false
      },
      throttling: {
        rttMs: 150,
        throughputKbps: 1638.4,
        cpuSlowdownMultiplier: 4
      }
    });

    console.log('=== LIGHTHOUSE MOBILE SCORES ===\n');

    const categories = ['performance', 'accessibility', 'best-practices', 'seo'];
    let allPassing = true;
    const results = {};

    for (const cat of categories) {
      const score = Math.round(lhr.categories[cat].score * 100);
      const status = score >= 90 ? '✓' : '✗';
      if (score < 90) allPassing = false;
      results[cat] = score;
      console.log(`${status} ${cat}: ${score}`);
    }

    console.log('');

    // Show failing audits
    if (!allPassing) {
      console.log('=== ISSUES TO FIX ===\n');

      const issues = [];
      for (const auditId of Object.keys(lhr.audits)) {
        const audit = lhr.audits[auditId];
        if (audit.score !== null && audit.score < 1 && audit.scoreDisplayMode !== 'informative') {
          if (['performance', 'accessibility'].some(cat =>
            lhr.categories[cat].auditRefs.some(ref => ref.id === auditId && ref.weight > 0)
          )) {
            issues.push({
              title: audit.title,
              score: audit.score,
              description: audit.description?.split('[')[0].trim()
            });
          }
        }
      }

      issues.sort((a, b) => a.score - b.score);
      for (const issue of issues.slice(0, 10)) {
        console.log(`- ${issue.title}`);
      }
    }

    // Performance metrics
    console.log('\n=== PERFORMANCE METRICS ===\n');
    const metrics = [
      'first-contentful-paint',
      'largest-contentful-paint',
      'total-blocking-time',
      'cumulative-layout-shift',
      'speed-index'
    ];

    for (const metric of metrics) {
      const audit = lhr.audits[metric];
      if (audit) {
        console.log(`${audit.title}: ${audit.displayValue}`);
      }
    }

    return { allPassing, results };
  } finally {
    await browser.close();
    server.close();
  }
}

runLighthouse()
  .then(({ allPassing }) => {
    console.log('\n' + (allPassing ? 'All scores >= 90!' : 'Some scores need improvement.'));
    process.exit(allPassing ? 0 : 1);
  })
  .catch(err => {
    console.error('Error:', err);
    process.exit(1);
  });
