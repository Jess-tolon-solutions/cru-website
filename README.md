# Ceilings R Us — Website

Custom content blocks for **ceilingsrus.net** (WordPress + **Flatsome** theme).
Single source of truth for the site's hand-built sections and pages.

## How edits reach the live site

The site is edited in the **Flatsome UX Builder**. Each block here is a
self-contained `<style>` + HTML snippet that gets **pasted into an HTML element**
(UX Builder → HTML element, or a Custom HTML block). We paste content, not files —
there is **WP-admin access only, no hosting/SFTP**.

Typical flow: copy a file's contents → in UX Builder click the target HTML element →
`Cmd+A` → `Cmd+V` → **Apply** → **Update** → hard-refresh (`Cmd+Shift+R`).

> The **Violation Map** is the exception — it's an `<iframe>` (see
> `pages/violation-map-embed.html`) pointing at GitHub Pages in the
> `ceilings-ru-assessment-` repo, which auto-refreshes DBPR data every Monday.
> That tool + its data pipeline live in that repo, **not** here.

---

## File Structure

```
cru-website/
├── README.md
├── shared/
│   ├── styles.css            # Brand palette & canonical facts
│   ├── site-styles.css       # Site-wide CSS (load via WPCode)
│   └── components.html       # Reusable component reference
├── homepage/
│   ├── before-after.html     # Violation-to-inspection-ready showcase
│   ├── tools-3card.html      # Free compliance tools cards
│   └── trust-strip.html      # Condensed trust strip
├── pages/
│   ├── contact.html          # Contact page with modal form
│   ├── real-violations.html  # Interactive flip-card violations guide
│   ├── privacy.html          # Privacy policy
│   ├── terms.html            # Terms & conditions
│   ├── violation-map-embed.html  # Iframe embed for DBPR map
│   ├── headers/              # H1 snippets for pages missing them
│   │   ├── h1-miami.html
│   │   ├── h1-miami-dade.html
│   │   ├── h1-fort-lauderdale.html
│   │   ├── h1-broward-county.html
│   │   ├── h1-west-palm-beach.html
│   │   ├── h1-boca-raton.html
│   │   ├── h1-about.html
│   │   ├── h1-why.html
│   │   ├── h1-mission-values.html
│   │   ├── h1-our-story.html
│   │   ├── h1-violation-map.html
│   │   ├── h1-facility-assessment.html
│   │   ├── h1-real-violations.html
│   │   ├── h1-blogs.html
│   │   └── h1-contact.html
│   ├── templates/            # Base templates for page types
│   │   ├── location-page.html
│   │   └── service-page.html
│   ├── locations/            # Location landing pages
│   │   ├── miami.html
│   │   ├── miami-dade.html
│   │   ├── fort-lauderdale.html
│   │   ├── broward-county.html
│   │   ├── west-palm-beach.html
│   │   └── boca-raton.html
│   ├── services/             # Service pages
│   │   ├── services-hub.html
│   │   ├── commercial-ceiling-cleaning.html
│   │   ├── ceiling-restoration.html
│   │   ├── ventilation-duct-cleaning.html
│   │   ├── inspection-preparation.html
│   │   ├── general-cleaning.html
│   │   ├── specialized-cleaning.html
│   │   └── post-construction-cleaning.html
│   ├── industries/           # Industry-specific pages
│   │   ├── grocery-ceiling-cleaning.html
│   │   └── hotel-ceiling-cleaning.html
│   └── about/                # About section pages
│       ├── about.html
│       ├── why.html
│       ├── our-story.html
│       └── mission-values.html
├── footer/
│   └── footer.html           # Site footer (Local-SEO focused)
└── seo/
    ├── title-description-map.md   # SEO audit & recommendations
    ├── title-description-map.html # Interactive SEO worksheet
    └── yoast-updates.md           # Copy-paste ready Yoast content
```

---

## What's Where

### Homepage Sections

| File | Goes on | Notes |
|---|---|---|
| `homepage/before-after.html` | Home (below logo scroll) | "Violation to Inspection-Ready" — mold → cleaned |
| `homepage/tools-3card.html` | Home (Free Compliance Tools) | Assessment · Violation Map · What an Inspector Sees |
| `homepage/trust-strip.html` | Home (below tools) | Condensed 5-point trust bar |

### Page Templates & Content

| File | URL | Notes |
|---|---|---|
| `pages/real-violations.html` | `/real-violations/` | 6 flip cards with violation details |
| `pages/violation-map-embed.html` | `/violation-map/` | Iframe + header CSS |
| `pages/contact.html` | `/contact/` | Contact form with Jobber modal |
| `pages/privacy.html` | `/privacy-policy/` | Approved content |
| `pages/terms.html` | `/terms-and-conditions/` | FL governing law |

### Location Pages

| File | URL |
|---|---|
| `pages/locations/miami.html` | `/miami/` |
| `pages/locations/miami-dade.html` | `/miami-dade/` |
| `pages/locations/fort-lauderdale.html` | `/fort-lauderdale/` |
| `pages/locations/broward-county.html` | `/broward-county/` |
| `pages/locations/west-palm-beach.html` | `/west-palm-beach/` |
| `pages/locations/boca-raton.html` | `/boca-raton/` |

### Service Pages

| File | URL |
|---|---|
| `pages/services/services-hub.html` | `/services/` |
| `pages/services/commercial-ceiling-cleaning.html` | `/commercial-ceiling-cleaning/` |
| `pages/services/ceiling-restoration.html` | `/ceiling-restoration/` |
| `pages/services/ventilation-duct-cleaning.html` | `/ventilation-and-duct-cleaning/` |
| `pages/services/inspection-preparation.html` | `/inspection-preparation/` |
| `pages/services/general-cleaning.html` | `/general-cleaning/` |
| `pages/services/specialized-cleaning.html` | `/specialized-cleaning-solutions/` |
| `pages/services/post-construction-cleaning.html` | `/post-construction-cleaning/` |

### Industry Pages

| File | URL |
|---|---|
| `pages/industries/grocery-ceiling-cleaning.html` | `/grocery-ceiling-cleaning/` |
| `pages/industries/hotel-ceiling-cleaning.html` | `/hotel-ceiling-cleaning/` |

### About Pages

| File | URL |
|---|---|
| `pages/about/about.html` | `/about/` |
| `pages/about/why.html` | `/why/` |
| `pages/about/our-story.html` | `/our-story/` |
| `pages/about/mission-values.html` | `/mission-values/` |

### SEO & Reference

| File | Purpose |
|---|---|
| `seo/title-description-map.md` | SEO audit for all 29 pages |
| `seo/yoast-updates.md` | Copy-paste ready titles & descriptions |
| `shared/styles.css` | Brand palette & canonical facts |
| `shared/site-styles.css` | Site-wide CSS (load via WPCode) |
| `shared/components.html` | Reusable component reference |

---

## Brand Quick-Reference

**Colors:**
- Primary teal: `#116782`
- Dark teal: `#0f2d36`
- Green CTA: `#5eff00`
- Body text: `#374151`
- Muted: `#5a7580`
- Light BG: `#f4f8f9`

**Fonts:** Open Sans (site), Inter (violation cards)

**Contact:**
- Phone: (954) 452-0004
- Email: info@ceilingsrus.net
- Address: 2880 SW 23rd Terrace, Ste 104, Fort Lauderdale, FL 33312

**Key Page IDs:**
- Home: `page-id-21`
- Violation Map: `page-id-1561`
- Facility Assessment: `page-id-1556`
- Real Violations: `page-id-1633`

---

## Deployment Notes

### For Page Templates
1. Copy the entire file contents
2. In WP-admin, go to the page in UX Builder
3. Add an HTML element (or select existing)
4. Paste the content
5. Apply → Update → Hard refresh

### For H1 Headers
1. Copy the H1 snippet for the page
2. Paste into UX Builder at the top of the page content
3. Apply → Update

### For SEO Updates
1. Open `seo/yoast-updates.md`
2. Copy the title and description for each page
3. Paste into Yoast SEO box on each page
4. Save → Purge SiteGround cache

---

## Still Open

- [ ] Hero: black overlay (~40%, Flatsome section Overlay) + mobile optimization
- [ ] Verify all location/service page hero images exist in WordPress media library
- [ ] 301 redirect: `/ventilation-and-air-duct-cleaning/` → `/ventilation-and-duct-cleaning/`
- [ ] Fix double H1 on `/ventilation-and-duct-cleaning/` in Flatsome

---

## Last Updated

2026-07-21 — Major update: Added location pages (6), service pages (8), industry pages (2), about pages (4), H1 headers (15), SEO copy document, and design system enhancements.
