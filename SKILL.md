---
name: generate-llms-txt
description: >-
  Audits a website and drafts llms.txt plus robots.txt hints for AI crawlers.
  Use when the user asks to create, update, or optimize llms.txt, LLM site map,
  AIO, or AI-readable site index for a blog, docs site, or corporate site.
disable-model-invocation: true
---

# Generate llms.txt for a website

Help the user produce a production-ready `llms.txt` at the site root and a
`robots.txt` comment pointing to it. `llms.txt` is an emerging convention: a
short, human- and LLM-readable index so agents understand the site without
full crawling.

## Before you start

Ask only if missing:

1. **Site URL** (e.g. `https://example.com`)
2. **Site type** — blog | corporate | docs | e-commerce | knowledge base
3. **Primary language** of public content
4. **Audience** in one sentence (who reads this site and why)

## Workflow

Copy this checklist and track progress:

```
- [ ] Step 1: Discover site structure
- [ ] Step 2: Pick sections and key pages
- [ ] Step 3: Draft llms.txt
- [ ] Step 4: Draft robots.txt snippet
- [ ] Step 5: Validate and deliver
```

### Step 1: Discover site structure

Prefer, in order:

1. `https://<host>/sitemap.xml` or `sitemap_index.xml` — list URLs and infer sections
2. Homepage navigation + footer links
3. `https://<host>/robots.txt` — note existing rules and sitemap line
4. Existing `https://<host>/llms.txt` — if present, improve rather than replace blindly

If the user has a local repo, also scan `README`, `docs/`, and routing config.

Do **not** invent URLs. Every link in output must be verified or marked
`<!-- TODO: verify URL -->`.

### Step 2: Pick sections and key pages

Rules:

- Group links under `## Section` headings that match how humans browse (Products,
  Docs, Blog, Support — not internal codenames).
- **5–12 links per section**; prefer evergreen, high-signal pages over news churn.
- Each link: `[Title](absolute-url)` plus optional `: one-line description` (≤160 chars).
- Descriptions must add facts the title alone does not convey.
- Include: About, Contact, Privacy/Terms if they exist.
- Exclude: login, cart, search results, paginated archives, `?replytocom`, staging.

### Step 3: Draft llms.txt

Use this structure (see [template-llms.txt](template-llms.txt)):

```markdown
# Site Name

> One-line tagline or site description from meta/hero.

2–4 sentences: what the site is, who it serves, what topics it covers, who runs it.

Last updated: YYYY-MM-DD

## Section Name

- [Page title](https://example.com/path/): Short factual description.
```

Language: match the site's primary public language. Mixed-language sites may use
bilingual section titles if that reflects reality.

Keep total file **under ~8 KB** — an index, not a sitemap dump.

### Step 4: Draft robots.txt snippet

Produce a **comment block** the user can paste into existing `robots.txt`:

```text
# LLM site map (human/LLM-readable index)
# https://example.com/llms.txt
```

If there is no `Sitemap:` line yet, add:

```text
Sitemap: https://example.com/sitemap.xml
```

Do **not** overwrite the user's full `robots.txt` unless they explicitly ask.
List AI user-agents (`GPTBot`, `ClaudeBot`, `PerplexityBot`, etc.) only when
the user wants an explicit opt-in/opt-out policy.

### Step 5: Validate and deliver

Checklist before handing off:

- [ ] `#` title matches site branding
- [ ] All URLs are absolute `https://`
- [ ] `Last updated` is today's date
- [ ] No duplicate links
- [ ] Descriptions are factual, not marketing fluff
- [ ] File is valid Markdown (headings, list syntax)

Deliver:

1. Complete `llms.txt` in a fenced code block (or write to `llms.txt` in the project if asked)
2. `robots.txt` snippet to paste
3. **Deploy note:** upload `llms.txt` to the **web root** so `https://<host>/llms.txt` returns `text/plain` or `text/markdown`. WordPress, static hosts, and CDNs differ — give steps for the user's stack if known.
4. Optional: 3 concrete next steps (Schema.org, FAQ blocks, internal linking)

## Reference

- Working example: [example-llms.txt](example-llms.txt) (blog.bezpalov.com)
- Empty template: [template-llms.txt](template-llms.txt)
- Background post: https://blog.bezpalov.com/optimize-site-for-ai/

## Do not

- Claim `llms.txt` is an IETF/W3C standard — say *emerging convention*
- Block all AI bots by default without the user asking
- Dump every sitemap URL into the file
- Include credentials, staging hosts, or private admin paths
