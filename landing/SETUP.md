# Direct Mail Landing Page — Setup Checklist

## V36 Pilot Campaign (290 restaurants: Broward, Palm Beach, Miami Shores/MiMo)

---

## 1. WordPress Page Setup

1. **Create the page**
   - Go to **Pages → Add New**
   - Title: `Free Ceiling Check`
   - Slug: `free-ceiling-check`
   - Template: **Blank (no header/footer)** or a minimal template
   - Publish

2. **Add the snippet via WPCode**
   - Go to **Code Snippets → Add Snippet**
   - Name: `Direct Mail Landing - V36 Pilot`
   - Code Type: **HTML Snippet**
   - Paste the contents of `/landing/free-ceiling-check/snippet.html`
   - Location: **Shortcode**
   - Save and copy the shortcode (e.g., `[wpcode id="123"]`)

3. **Insert into the page**
   - Edit the page, add a **Shortcode** block
   - Paste the WPCode shortcode
   - Update the page

4. **Set noindex**
   - In Yoast/RankMath, set the page to **noindex, nofollow**
   - Or verify the `<meta name="robots" content="noindex, nofollow">` is in the snippet

5. **Upload hero image**
   - Upload `/landing/assets/hero-dining.webp` to Media Library
   - Note the URL (e.g., `https://ceilingsrus.net/wp-content/uploads/2026/dm/hero-dining.webp`)
   - Update the image URL in the snippet

---

## 2. Redirects (Redirection Plugin)

Create **three 302 redirects** (temporary, so they can be changed later without reprinting):

| Source URL | Target URL |
|------------|-----------|
| `/mail-bro` | `/free-ceiling-check/?code=MAIL10-BRO&utm_source=directmail&utm_medium=postcard&utm_campaign=v36-pilot&utm_content=broward` |
| `/mail-pb` | `/free-ceiling-check/?code=MAIL10-PB&utm_source=directmail&utm_medium=postcard&utm_campaign=v36-pilot&utm_content=palmbeach` |
| `/mail-mia` | `/free-ceiling-check/?code=MAIL10-MIA&utm_source=directmail&utm_medium=postcard&utm_campaign=v36-pilot&utm_content=miamishores` |

**In the Redirection plugin:**
1. Go to **Tools → Redirection**
2. Add each redirect with:
   - Source: the short URL path
   - Target: the full target with query params
   - HTTP Code: **302 Temporary**

---

## 3. Form & Lead Flow

The form now uses **Jobber's embedded form** (same as the site's quote modal), so all leads flow directly into Jobber.

**Jobber Form ID:** `a022635a-e1bc-43e3-bbac-6e97a2584f23-4837330`

**Promo Code Tracking:**
- The promo code from the URL (`?code=MAIL10-BRO`) is displayed above the form
- Customers are prompted to mention it when you call
- You can track which region leads came from via the code:
  - `MAIL10-BRO` → Broward
  - `MAIL10-PB` → Palm Beach
  - `MAIL10-MIA` → Miami Shores/MiMo

**Optional: Zapier Integration**
If you also want leads to flow to Monday.com, you can set up a Zapier automation:
1. Trigger: New Jobber Lead
2. Filter: Lead source contains "Direct Mail" or promo code starts with "MAIL10"
3. Action: Create Monday.com item in "Website Leads" → "Direct Mail" group

---

## 4. GA4 Setup

1. Go to **GA4 → Admin → Events**

2. Mark these events as **Key Events** (conversions):
   - `generate_lead`
   - `click_to_call`

3. Create custom dimensions if you want to segment:
   - `promo_code` (event-scoped)
   - `link_location` (event-scoped)

---

## 5. Testing Checklist

### QR Code Verification
- [ ] Scan `/landing/qr/qr-bro.svg` → lands on `/free-ceiling-check/?code=MAIL10-BRO...`
- [ ] Scan `/landing/qr/qr-pb.svg` → lands on `/free-ceiling-check/?code=MAIL10-PB...`
- [ ] Scan `/landing/qr/qr-mia.svg` → lands on `/free-ceiling-check/?code=MAIL10-MIA...`

### URL Parameter Handling
- [ ] Visit with `?code=MAIL10-BRO` → code displays in hero and form
- [ ] Visit without code → shows default "MAIL10"
- [ ] UTM params are captured in hidden form fields

### Form Submission
- [ ] Required field validation works
- [ ] Submit test lead with valid data
- [ ] Confirm lead appears in Monday.com "Direct Mail" group
- [ ] Success message shows correct promo code

### GA4 Events (use DebugView)
- [ ] Click any phone link → `click_to_call` fires with correct `link_location`
- [ ] Submit form → `generate_lead` fires with `promo_code` and `utm_content`

### Mobile Experience
- [ ] Page loads correctly at 390px width
- [ ] Sticky call bar visible at bottom
- [ ] Form fields are easy to tap
- [ ] Scroll to form works from hero button

---

## 6. Print Assets

### QR Codes (print-ready SVG, error correction M, no margin)
- `/landing/qr/qr-bro.svg` → `https://ceilingsrus.net/mail-bro`
- `/landing/qr/qr-pb.svg` → `https://ceilingsrus.net/mail-pb`
- `/landing/qr/qr-mia.svg` → `https://ceilingsrus.net/mail-mia`

**Verified URLs (decoded from QR codes):**
```
✓ qr-bro.svg: https://ceilingsrus.net/mail-bro
✓ qr-pb.svg: https://ceilingsrus.net/mail-pb
✓ qr-mia.svg: https://ceilingsrus.net/mail-mia
```

---

## Files in This Package

```
/landing/
├── free-ceiling-check/
│   ├── snippet.html      # WPCode snippet (copy this to WordPress)
│   └── preview.html      # Local preview file
├── qr/
│   ├── qr-bro.svg        # Broward QR code
│   ├── qr-pb.svg         # Palm Beach QR code
│   └── qr-mia.svg        # Miami Shores QR code
├── assets/
│   ├── hero-dining.webp  # Hero image (82 KB)
│   ├── hero-a.webp       # Team cleaning photo (140 KB)
│   ├── hero-b.webp       # Kitchen cleaning photo (156 KB)
│   ├── prep.webp         # Table prep photo (137 KB)
│   └── logo.png          # Circular logo badge
├── build-assets.js       # Asset build script
├── SETUP.md              # This file
└── package.json
```

---

## Items to Confirm with Jonathan

These are marked in the HTML with `<!-- CONFIRM WITH JONATHAN -->` comments:

1. **Ceiling check duration**: "A 20-minute look up" — is 20 minutes accurate?
2. **What the ceiling check includes**: Walking dining room and kitchen, showing what we see, giving a price
3. **Ceiling types**: "Acoustic tile, drop ceilings, exposed and painted surfaces" — any others?
4. **Response time**: "We'll call you within one business day" — is this the SLA?

---

## Compliance Reminders (DO NOT CHANGE)

- ❌ No mention of health inspection violations or citations
- ❌ No kitchen exhaust/hood cleaning (not offered yet)
- ❌ No mold claims or mold removal language
- ✅ All claims stick to approved facts only
