---
name: generate-llms-txt
description: >-
  Audits a website and drafts a curated llms.txt plus robots.txt notes for AI
  crawlers. Use when the user asks to create, update, or optimize llms.txt,
  LLM site map, AIO layer 2, or AI-readable site index for a blog, docs, or
  corporate site.
disable-model-invocation: true
---

# Generate llms.txt for a website

Help the user produce a **curated** production-ready `llms.txt` at the site root
and a short `robots.txt` note. `llms.txt` is an **emerging convention**
([llmstxt.org](https://llmstxt.org/)), not an IETF/W3C standard: a short human-
and LLM-readable index so agents understand the site without a full crawl.

**Curated ≠ sitemap dump.** Auto-generated dumps (e.g. SEO plugins listing every
post) defeat the purpose. Prefer evergreen, high-signal pages. Full URL inventory
belongs in `sitemap.xml`.

This skill is **layer 2** of AIO (see [background](https://blog.bezpalov.com/optimize-site-for-ai/)).
For a full three-layer audit use `@aio-site-audit`. For Schema.org drafts use
`@draft-json-ld`. For AI bot policy in robots.txt use `@audit-robots-ai-bots`.

## Before you start

Ask only if missing:

1. **Site URL** (e.g. `https://example.com`) — public `https` only
2. **Site type** — blog | corporate | docs | e-commerce | knowledge base
3. **Primary language** of public content
4. **Audience** in one sentence

**Safety:** do not fetch staging hosts, admin paths, or anything behind auth.
No cookies, tokens, or custom auth headers. Public pages only.

## Workflow

```
- [ ] Step 1: Discover site structure
- [ ] Step 2: Pick sections and key pages
- [ ] Step 3: Draft llms.txt (llmstxt.org shape)
- [ ] Step 4: robots.txt note (human comment, not a directive)
- [ ] Step 5: Validate and deliver
```

### Step 1: Discover site structure

Prefer, in order:

1. `https://<host>/sitemap.xml` or `sitemap_index.xml` — infer sections; do not dump all URLs
2. Homepage navigation + footer
3. `https://<host>/robots.txt` — note existing rules and `Sitemap:`
4. Existing `https://<host>/llms.txt` — if present, **improve curation**; if it is a
   bulk dump, propose a curated replacement and explain why

If the user has a local repo, also scan `README`, `docs/`, and routing config.

For **docs** sites: prefer links to clean Markdown twins (`page.md` / `index.html.md`)
when they exist ([llmstxt.org](https://llmstxt.org/) proposal).

Do **not** invent URLs. Every link must be verified or marked `<!-- TODO: verify URL -->`.

### Step 2: Pick sections and key pages

- Group under `## Section` headings that match human browsing (Products, Docs, Blog,
  Support — not internal codenames).
- **5–12 links per section**; evergreen over news churn.
- Each link: `[Title](absolute-url)` plus optional `: one-line description` (≤160 chars).
- Include About, Contact, Privacy/Terms if they exist.
- Exclude: login, cart, search results, paginated archives, `?replytocom`, staging.
- Put secondary / skippable links under `## Optional` (llmstxt.org special section —
  agents may omit these when context is tight).

### Step 3: Draft llms.txt

Follow [llmstxt.org](https://llmstxt.org/) order (see [template-llms.txt](template-llms.txt)):

```markdown
# Site Name

> One-line tagline or site description from meta/hero.

2–4 sentences: what the site is, who it serves, topics, who runs it.

Last updated: YYYY-MM-DD

## Section Name

- [Page title](https://example.com/path/): Short factual description.

## Optional

- [Secondary page](https://example.com/secondary/): Skippable if context is limited.
```

Language: match the site's primary public language.

Keep total file **under ~8 KB** — an index, not a sitemap dump.

### Step 4: robots.txt note

Produce a **comment block** the user can paste into existing `robots.txt`:

```text
# LLM-oriented site map (human/editor note — not a crawler directive)
# Discovery for agents: https://example.com/llms.txt at the site root
# https://example.com/llms.txt
```

Important: a `#` line in `robots.txt` is **not** a directive. Bots do not discover
`llms.txt` through comments. Discovery = file at `https://<host>/llms.txt`.
`Sitemap:` only applies to XML sitemaps.

If there is no `Sitemap:` line yet, suggest:

```text
Sitemap: https://example.com/sitemap.xml
```

Do **not** overwrite the full `robots.txt` unless asked.
Do **not** add AI user-agent allow/deny blocks here — hand off to `@audit-robots-ai-bots`
when the user wants an explicit bot policy.

### Step 5: Validate and deliver

- [ ] `#` title matches branding
- [ ] Absolute `https://` URLs only
- [ ] `Last updated` is today
- [ ] No duplicates; factual descriptions
- [ ] Valid Markdown; size ≲ 8 KB
- [ ] `## Optional` used only for secondary links (if any)

Deliver:

1. Complete `llms.txt` (fenced block or write file if asked)
2. `robots.txt` comment snippet
3. Deploy note: file at **web root** so `/llms.txt` returns `text/plain` or `text/markdown`
4. Optional next steps: `@draft-json-ld`, `@audit-robots-ai-bots`, `@aio-site-audit`

## Reference

- Curated example: [example-llms.txt](example-llms.txt) (golden sample — not a plugin dump)
- Template: [template-llms.txt](template-llms.txt)
- Spec: https://llmstxt.org/
- AIO background: https://blog.bezpalov.com/optimize-site-for-ai/

## Do not

- Claim `llms.txt` is an IETF/W3C standard — say *emerging convention*
- Treat SEO-plugin dumps as a good final `llms.txt`
- Block all AI bots by default without the user asking
- Dump every sitemap URL into the file
- Include credentials, staging hosts, or private admin paths
- Imply that a robots.txt comment makes crawlers fetch `llms.txt`
