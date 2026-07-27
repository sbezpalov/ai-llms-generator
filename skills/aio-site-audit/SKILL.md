---
name: aio-site-audit
description: >-
  Orchestrates a three-layer AIO audit: robots.txt (AI crawlers), curated
  llms.txt, and Schema.org JSON-LD. Use when the user asks for AIO, AI SEO
  audit, optimize site for AI, AI Overviews readiness, or a full site check
  for LLM agents.
disable-model-invocation: false
---

# AIO site audit (orchestrator)

Run a **three-layer** readiness audit so AI agents and people both understand
the site. Formula from
[optimize-site-for-ai](https://blog.bezpalov.com/optimize-site-for-ai/):

> clear content + structure + `robots.txt` + curated `llms.txt` + Schema.org

This skill **orchestrates**. For deep drafts, follow or invoke:

| Layer | Concern | Specialist skill |
|-------|---------|------------------|
| 1 | Who may crawl / AI bot policy | `@audit-robots-ai-bots` |
| 2 | Curated meaning map | `@generate-llms-txt` |
| 3 | Machine passport (JSON-LD) | `@draft-json-ld` |

## Before you start

Ask only if missing:

1. **Site URL** (public `https` only)
2. **Site type** and primary language
3. Whether the user wants **audit only** or **audit + drafts**

**Safety:** public fetches only; no auth/staging; do not push live changes
without confirmation.

## Workflow

```
- [ ] L0 Content & structure smoke check
- [ ] L1 robots.txt + AI agents
- [ ] L2 llms.txt (curated vs dump)
- [ ] L3 JSON-LD presence / gaps
- [ ] Scorecard + next actions
```

### L0 — Content & structure (smoke)

From homepage + 1–2 key URLs, note only:

- Clear H1 / title?
- Visible author or org?
- Obvious nav / internal links?
- Important text reachable without login?

Do not rewrite the whole site here — flag gaps.

### L1 — robots.txt

- Fetch `/robots.txt`
- Summarize allow/deny and `Sitemap:`
- Note AI user-agents if present
- Remind: `# llms.txt` comments are **not** directives

If policy changes are needed → `@audit-robots-ai-bots`.

### L2 — llms.txt

- Fetch `/llms.txt` (404 = missing)
- Classify: **missing** | **curated** | **bulk dump** (plugin/sitemap-like)
- Bulk dump = recommend curated rewrite via `@generate-llms-txt`
- Check approximate size (warn if huge) and absolute https links

### L3 — Schema.org

- On home + one article (if blog): look for `application/ld+json`
- Note types found vs expected (Organization / WebSite / Article / FAQ…)
- Gaps → `@draft-json-ld`

### Scorecard deliverable

Present a compact table:

| Layer | Status | Evidence | Priority fix |
|-------|--------|----------|--------------|
| L0 Content | ok / weak / fail | … | … |
| L1 robots | … | … | … |
| L2 llms.txt | missing / curated / dump | … | … |
| L3 JSON-LD | … | … | … |

Then **top 3 actions** in order of impact. Offer to run specialist skills next.

Optional: 5-item publish checklist from the article (title/H1, summary/FAQ,
author+dates, schema, sitemap, robots, llms.txt, internal links) — mark each.

## Do not

- Treat Rank Math / SEO plugin URL dumps as a finished L2
- Claim `llms.txt` is an IETF/W3C standard — *emerging convention*
- Block all AI bots without an explicit user decision
- Invent Schema ratings or contact data
- Modify production files unless the user asks
