# In-Person Leave-Behind Campaign

Print leave-behinds the crew hands to prospects, plus the landing page the QR opens.

**Design canvas (view / export PNG + PDF):**
https://claude.ai/code/artifact/4e4674d7-846d-4fc9-9574-d8f5a8d018c7

## What's here

| File | What it is |
|---|---|
| `Main.dc.html` | Option A front — restaurants & food service, 8.5×11 |
| `PropertyFront.dc.html` | Option B front — property & facility managers, 8.5×11 |
| `OfferBack.dc.html` | Shared back — QR + 10% off. Same on both options |
| `LandingPage.dc.html` | Landing page, desktop |
| `LandingMobile.dc.html` | Landing page, mobile (this is the one that matters — nearly every scan is a phone) |
| `canvas.json` | Canvas layout: page 1 = leave-behinds, page 2 = landing page |
| `*.jpg`, `logo.png` | Images, pulled from the live site and compressed for embedding |

The production landing page (real form, real code reveal) is **not** here — it lives at
`pages/campaigns/in-person-10-off.html` with the rest of the site blocks.

## Print specs

- **8.5 × 11, double-sided.** Both fronts share one back, so only one back ever goes to print.
- 100lb gloss text (cheap, flexible) or 14pt cover (feels like a real leave-behind).
- Ask for **0.125" bleed** — the header, hero and footer all run to the edge.
- Authored at 96 px/inch (816 × 1056 px = 8.5 × 11 in).

## The QR code

Encodes **`https://ceilingsrus.net/10-off/`** at error-correction level H.

That page has to exist before anything goes to print. Changing the slug means
reprinting, so the slug is frozen once the first batch is ordered.

**No expiry date on this campaign** — deliberate (2026-08-30), so printed brochures never
go stale sitting in a drawer. The fine print says "new customers only, one per location"
and stops there.

## Before printing — open items

- [ ] Build `/10-off/` in WordPress from `pages/campaigns/in-person-10-off.html`
- [ ] Activate the form endpoint — leads go to info@ceilingsrus.net, but FormSubmit needs a
      one-time confirmation click before it will deliver anything (see the file header)
- [ ] Scan the printed proof with a real phone before approving the full run

## Rebuilding the canvas

The seeded `.html` is a build output and is gitignored — regenerate it from these files:

```bash
cd print/in-person-campaign
node "<design skill dir>/seed-canvas.mjs" \
  --template "<design skill dir>/payload.template.html" \
  --out ceilings-r-us-in-person-kit.html \
  --title "Ceilings R Us In-Person Kit" \
  --artboard Main.dc.html --artboard PropertyFront.dc.html --artboard OfferBack.dc.html \
  --artboard LandingPage.dc.html --artboard LandingMobile.dc.html \
  --image hero-a.jpg --image hero-b.jpg --image before.jpg --image after.jpg \
  --image prep.jpg --image logo.png \
  --canvas canvas.json
```

Then republish to the same artifact URL to keep the link stable.
