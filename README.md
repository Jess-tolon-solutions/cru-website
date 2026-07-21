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

## What's where

| File | Goes on | Notes |
|---|---|---|
| `homepage/before-after.html` | Home (below logo scroll) | "Violation to Inspection-Ready" — mold → cleaned, Code 36 flag |
| `homepage/trust-strip.html` | Home (below tools) | condensed 5-point trust bar |
| `homepage/tools-3card.html` | Home (Free Compliance Tools) | Assessment · Violation Map · What an Inspector Sees |
| `pages/real-violations.html` | `/real-violations/` | 6 flip cards, accurate "Basic · Code 36 / Escalates To" framing |
| `pages/violation-map-embed.html` | `/violation-map` (page-id-1561) | iframe + header CSS (keep header height = padding-top, logo smaller) |
| `pages/privacy.html` | Privacy page | approved content, Last Updated 2026-06-19 |
| `pages/terms.html` | Terms page | approved content, FL governing law |
| `footer/` | site footer | (in progress — Local-SEO focused) |
| `seo/title-description-map.md` | Yoast (per-page) | title + meta description recommendations for all 29 pages (audited 2026-07-21); `.html` = interactive worksheet |
| `shared/styles.css` | — | brand palette + canonical facts (phone, email, page IDs) |

## Brand quick-reference

- **Colors:** teal `#116782` / dark `#0f2d36` / green CTA `#5eff00`; body `#374151` on `#f4f8f9`
- **Fonts:** Open Sans (site), Inter (violation cards)
- **Phone:** (954) 452-0004 · **Email:** info@ceilingsrus.net
- **Home** = `page-id-21`, **Violation Map** = `page-id-1561`

## Still open
- Hero: black overlay (~40%, Flatsome section Overlay) + mobile optimization
- Footer: rebuild with Local-SEO focus (was deleted)
- Contact page: update
