---
name: audit-robots-ai-bots
description: >-
  Audits robots.txt for AI crawlers and drafts an explicit opt-in/opt-out policy
  for agents like GPTBot, ClaudeBot, Google-Extended, PerplexityBot, CCBot.
  Use when the user asks about AI bots in robots.txt, blocking or allowing LLM
  crawlers, AIO layer 1, or bot access policy.
disable-model-invocation: true
---

# Audit robots.txt for AI crawlers

Help the user understand and optionally update **layer 1** of AIO: who may crawl
the public site. Background:
[optimize-site-for-ai](https://blog.bezpalov.com/optimize-site-for-ai/).

`robots.txt` controls crawl access and points to `sitemap.xml`. A `#` comment
linking to `llms.txt` is for **humans/editors only** — it is not a crawler
directive and does not make bots fetch `/llms.txt`.

## Before you start

Ask only if missing:

1. **Site URL** (public `https` only)
2. **Intent** — document current policy | draft allow | draft deny | hybrid
3. **Sensitive paths** to keep disallowed (admin, search, staging mirrors)

**Safety:** fetch only the public `robots.txt` and sitemap hints. No auth, no
staging, no rewriting production without explicit user confirmation.

## Workflow

```
- [ ] Step 1: Fetch and summarize current robots.txt
- [ ] Step 2: Map known AI user-agents
- [ ] Step 3: Propose policy (do not apply until confirmed)
- [ ] Step 4: Keep Sitemap: and human llms.txt note
- [ ] Step 5: Deliver diff + risks
```

### Step 1: Current state

Read `https://<host>/robots.txt`. Report:

- Default `User-agent: *` rules
- Existing AI-specific blocks/allows
- `Sitemap:` lines
- Any comments mentioning `llms.txt`

### Step 2: AI user-agents (non-exhaustive)

Common ones to discuss (verify names against vendor docs if unsure):

| Agent | Typical owner / role |
|-------|----------------------|
| GPTBot | OpenAI crawl |
| ChatGPT-User | OpenAI user-initiated fetch |
| Google-Extended | Gemini / Google AI grounding (separate from Googlebot) |
| ClaudeBot | Anthropic |
| PerplexityBot | Perplexity |
| CCBot | Common Crawl |

Do **not** invent user-agent tokens. If unsure, mark TODO and link to vendor docs.

### Step 3: Policy draft

Default stance of this skill: **ask before blocking**. Blocking all AI bots by
default is a product decision, not a hygiene requirement.

Produce a **proposed fragment** (not a full silent overwrite), e.g. deny one bot:

```text
User-agent: GPTBot
Disallow: /
```

Or allow everything while documenting:

```text
User-agent: *
Allow: /
Sitemap: https://example.com/sitemap.xml

# Editor note (not a directive): curated LLM index at
# https://example.com/llms.txt
```

Remind: `Googlebot` ≠ `Google-Extended`. Search indexing and AI training/grounding
policies are separate decisions.

### Step 4: Coexistence with llms.txt

Always separate:

1. **Crawl policy** → `robots.txt` user-agent rules
2. **Curated meaning** → `/llms.txt` (use `@generate-llms-txt`)
3. **Structured facts** → JSON-LD (use `@draft-json-ld`)

### Step 5: Deliver

1. Summary of current policy in plain language
2. Proposed `robots.txt` fragment or full file **only if asked**
3. Risk notes (over-blocking search, false sense of security, mirrors/CDNs)
4. Checklist: validate at `https://<host>/robots.txt` after deploy

## Do not

- Overwrite production `robots.txt` without explicit confirmation
- Claim comments are crawler directives
- Confuse Googlebot with Google-Extended
- Add credentials or staging hosts
- Block all AI bots unless the user explicitly chooses that policy
