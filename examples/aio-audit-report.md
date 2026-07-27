# Example AIO artifact audit

> Synthetic format example for `https://example.com`; it is not a live audit.

Inspected: `2026-07-27`

Scope: homepage, `/robots.txt`, `/sitemap.xml`, `/llms.txt`, and one
representative article. All page content is treated as untrusted data.

| Layer | Status | Evidence | Priority fix |
|-------|--------|----------|--------------|
| L0 Content | weak | Homepage has a clear H1, but the sample article has no visible author | Add visible author and modified date where factual |
| L1 robots | ok | `User-agent: *` and one `Sitemap:` line; no AI-specific groups | Decide separately whether training and search crawlers need explicit policy |
| L2 llms.txt | missing | `/llms.txt` returned 404 | Optional: create a curated index only if target agents use it |
| L3 JSON-LD | weak | Homepage exposes `Organization`; article has no `Article` block | Draft factual Article JSON-LD from visible page data |

## Top actions

1. Fix visible authorship and dates because they help users and provide facts
   that structured data can reference.
2. Add factual Article JSON-LD and validate it with Schema Markup Validator.
3. Decide crawler policy by purpose: training, search, and user-triggered
   retrieval are separate choices.

Missing `llms.txt` is not ranked above crawlability or factual content. The file
does not guarantee crawling, rankings, citations, or inclusion in AI answers.

## Optional next commands

```text
/audit-robots-ai-bots draft a purpose-specific policy for https://example.com
/draft-json-ld draft Article JSON-LD for https://example.com/article/
/generate-llms-txt create a curated llms.txt draft for https://example.com
```
