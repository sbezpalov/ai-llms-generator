---
name: draft-json-ld
description: >-
  Drafts Schema.org JSON-LD (Organization, Person, Article, FAQPage, HowTo,
  BreadcrumbList, WebPage) for AIO and SEO. Use when the user asks for
  microdata, structured data, JSON-LD, Schema.org, or AIO layer 3.
disable-model-invocation: true
---

# Draft Schema.org JSON-LD

Help the user add **layer 3** of AIO: machine-readable facts via JSON-LD.
Background: [optimize-site-for-ai](https://blog.bezpalov.com/optimize-site-for-ai/).

Prefer **JSON-LD** in `<script type="application/ld+json">` over microdata
attributes. Do not invent organization data — use values from the live page or
ask.

## Before you start

Ask only if missing:

1. **Page URL** (public `https`)
2. **Page type** — home | article/blog | FAQ | how-to | about/org | other
3. **Stack** — WordPress | static | Next.js | other (affects where to paste)

**Safety:** public pages only; no auth; do not scrape private admin.

## Type matrix

| Page kind | Primary `@type` | Often combine with |
|-----------|-----------------|--------------------|
| Blog post / article | `BlogPosting` or `Article` | `Person` author, `Organization` publisher |
| FAQ | `FAQPage` | — |
| Step-by-step guide | `HowTo` | — |
| Company / about | `Organization` | `WebSite`, `WebPage` |
| Author | `Person` | sameAs profiles |
| Any page with crumbs | `BreadcrumbList` | `WebPage` |
| Generic | `WebPage` | — |

## Workflow

```
- [ ] Step 1: Inspect page (title, dates, author, FAQ blocks)
- [ ] Step 2: Choose types from matrix
- [ ] Step 3: Draft JSON-LD (valid JSON)
- [ ] Step 4: Spot-check required properties
- [ ] Step 5: Deliver paste instructions for the user's stack
```

### Draft rules

- `@context`: `https://schema.org`
- Dates: full ISO 8601 with timezone when known (Google preference), not only `YYYY-MM-DD`
- `mainEntityOfPage` / `@id`: canonical page URL
- URLs absolute `https://`
- No marketing fluff in `description` — facts only
- If a property is unknown, omit it or mark TODO — do not fabricate ratings, reviews, or phone numbers

### Minimal Article shape

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "...",
  "description": "...",
  "author": { "@type": "Person", "name": "..." },
  "datePublished": "2026-06-14T15:26:32+03:00",
  "dateModified": "2026-06-14T15:26:32+03:00",
  "mainEntityOfPage": "https://example.com/post/"
}
```

More examples: [templates/](templates/).

### Deliver

1. One or more JSON-LD blocks ready to paste
2. Where to put them for the stated stack
3. Validation hint: Rich Results Test / Schema validator (user runs it)
4. Optional: suggest `@generate-llms-txt` and `@audit-robots-ai-bots` if those layers are missing

## Do not

- Invent awards, aggregate ratings, or fake FAQ
- Replace the user's entire theme/SEO plugin config unless asked
- Claim Schema alone replaces a curated `llms.txt`
- Include secrets or internal hostnames
