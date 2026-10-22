const sharp = require('sharp');
const QRCode = require('qrcode');
const jsQR = require('jsqr');
const fs = require('fs');
const path = require('path');

const assetsDir = path.join(__dirname, 'assets');
const qrDir = path.join(__dirname, 'qr');

// Convert JPG images to WebP
async function convertImages() {
  const images = ['hero-a.jpg', 'hero-b.jpg', 'prep.jpg'];

  for (const img of images) {
    const inputPath = path.join(assetsDir, img);
    const outputPath = path.join(assetsDir, img.replace('.jpg', '.webp'));

    if (fs.existsSync(inputPath)) {
      await sharp(inputPath)
        .resize(1200, null, { withoutEnlargement: true })
        .webp({ quality: 82 })
        .toFile(outputPath);

      const stats = fs.statSync(outputPath);
      console.log(`Converted ${img} → ${path.basename(outputPath)} (${Math.round(stats.size / 1024)} KB)`);
    }
  }

  // Also convert hero-dining.png if it exists
  const heroDining = path.join(assetsDir, 'hero-dining.png');
  if (fs.existsSync(heroDining)) {
    await sharp(heroDining)
      .resize(1200, null, { withoutEnlargement: true })
      .webp({ quality: 85 })
      .toFile(path.join(assetsDir, 'hero-dining.webp'));

    const stats = fs.statSync(path.join(assetsDir, 'hero-dining.webp'));
    console.log(`Converted hero-dining.png → hero-dining.webp (${Math.round(stats.size / 1024)} KB)`);
  }
}

// Generate QR codes
async function generateQRCodes() {
  const urls = [
    { url: 'https://ceilingsrus.net/mail-bro', filename: 'qr-bro.svg' },
    { url: 'https://ceilingsrus.net/mail-pb', filename: 'qr-pb.svg' },
    { url: 'https://ceilingsrus.net/mail-mia', filename: 'qr-mia.svg' }
  ];

  for (const { url, filename } of urls) {
    const svgString = await QRCode.toString(url, {
      type: 'svg',
      errorCorrectionLevel: 'M',
      margin: 0,
      width: 200
    });

    const outputPath = path.join(qrDir, filename);
    fs.writeFileSync(outputPath, svgString);
    console.log(`Generated ${filename} for ${url}`);
  }
}

// Verify QR codes by decoding them
async function verifyQRCodes() {
  const urls = [
    { url: 'https://ceilingsrus.net/mail-bro', filename: 'qr-bro.svg' },
    { url: 'https://ceilingsrus.net/mail-pb', filename: 'qr-pb.svg' },
    { url: 'https://ceilingsrus.net/mail-mia', filename: 'qr-mia.svg' }
  ];

  console.log('\n--- QR Code Verification ---');

  for (const { url, filename } of urls) {
    // Generate PNG version for verification
    const pngBuffer = await QRCode.toBuffer(url, {
      errorCorrectionLevel: 'M',
      margin: 1,
      width: 200
    });

    // Decode with sharp to get raw pixels
    const { data, info } = await sharp(pngBuffer)
      .ensureAlpha()
      .raw()
      .toBuffer({ resolveWithObject: true });

    // Convert to RGBA array
    const imageData = new Uint8ClampedArray(data);

    // Decode QR
    const decoded = jsQR(imageData, info.width, info.height);

    if (decoded && decoded.data === url) {
      console.log(`✓ ${filename}: VERIFIED → ${decoded.data}`);
    } else if (decoded) {
      console.log(`✗ ${filename}: MISMATCH → Got: ${decoded.data}, Expected: ${url}`);
    } else {
      console.log(`✗ ${filename}: FAILED TO DECODE`);
    }
  }
}

async function main() {
  console.log('Converting images to WebP...\n');
  await convertImages();

  console.log('\nGenerating QR codes...\n');
  await generateQRCodes();

  await verifyQRCodes();
}

main().catch(console.error);
