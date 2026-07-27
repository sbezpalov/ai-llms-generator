# aio-lint (v1.0)

Stdlib-only CLI that scores AIO artifacts for a **public https** site (or an
offline fixture). Ships in **ai-llms-generator v1.0.0**.

| Layer | Check |
|-------|--------|
| L0 | Homepage title / H1 / canonical / meta description |
| L1 | `robots.txt` reachability, `Sitemap:`, AI user-agent hints |
| L2 | `/llms.txt` missing / curated / dump (Rank Math-style heuristics) |
| L3 | Homepage `application/ld+json` `@type` presence |

It does **not** promise rankings, citations, or AI-answer inclusion. Fetched
HTML/text is untrusted data. SSRF controls: https-only, port 443, public DNS
IPs, same-host redirects, size + timeout limits.

## Usage

```bash
# Live site (network)
python scripts/aio_lint.py https://example.com
python scripts/aio_lint.py https://example.com --json --strict

# Offline fixtures (CI)
python scripts/aio_lint.py --fixture examples/aio-lint-fixtures/curated-site --expect-l2 curated
python scripts/aio_lint.py --fixture examples/aio-lint-fixtures/dump-site --expect-l2 dump
```

Exit codes: `0` success / expected classification, `1` lint or expect mismatch,
`2` usage or refused unsafe URL.

## GitHub Actions

Package CI runs fixture mode on every push. For a live URL, use workflow
`aio-lint-live` (`workflow_dispatch` input `url`).
