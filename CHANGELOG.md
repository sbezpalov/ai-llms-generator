# Changelog

All notable changes to this project are documented here.

The project uses semantic versioning for public releases.

## Unreleased

### Changed

- Documentation defaults to **English**; Russian mirrors use `*.ru.md`
  (`README.ru.md`, `PROMPT.ru.md`, `AGENTS.ru.md`, `CONTRIBUTING.ru.md`,
  `SECURITY.ru.md`)
- `generate-llms-txt` (skill + prompts): link verified Markdown page variants
  (llmstxt.org v2: `page.html.md` / `page.md`, `index.html.md` / `index.md`,
  `rel="alternate" type="text/markdown"`) for **any** site type, not only docs;
  guessed `.md` URLs stay forbidden
- `generate-llms-txt`: `Last updated:` is labelled a project convention; subpath
  files and the `text/plain` / `text/markdown` choice follow the proposal;
  `PROMPT.md` and `PROMPT.ru.md` re-aligned
- `audit-robots-ai-bots` + `aio-lint`: 13 more vendor-documented AI tokens
  (OpenAI ads, Google Vertex, Apple, Meta, Amazon, DuckDuckGo, Mistral) and the
  RFC 9309 rule that a bot-specific group replaces `User-agent: *`
- `draft-json-ld` templates use `TODO_REPLACE_*` placeholders instead of
  realistic sample values; `aio-lint` L3 warns when placeholders or
  `example.com` reach published JSON-LD
- `aio-site-audit`: L2 statuses match the linter, Markdown variants are noted,
  and the linter command is documented as run from a repository clone
- `PROMPT.en.md` (named in 0.1.0) is now `PROMPT.md`; the Russian prompt is
  `PROMPT.ru.md`

### Fixed

- `aio-lint` L2: link entries with `*`/`+` bullets, indentation, brackets in the
  title, parentheses in the URL or a dash separator are now counted, so such
  dumps are no longer missed
- `aio-lint` L2: an error response is never classified from its body — new
  `unavailable` classification for non-200 other than 404/410; a leading BOM is
  tolerated
- `aio-lint` L1: statuses follow RFC 9309 (4xx = no policy → `weak`, 5xx =
  complete disallow → `fail`); trailing comments are stripped and only absolute
  `Sitemap:` URLs count
- `aio-lint` L0/L3: attribute order and quoting no longer matter; `@graph`
  inside a top-level list and typed `application/ld+json; charset=…` are read
- `aio-lint`: credentials or a non-default port in the target are refused
  instead of being silently dropped

### Added

- `aio-lint` L2 reports an informational `markdown_links` count
- Offline `unittest` suite (`tests/`), run in CI
- `aio-lint --check-links`: opt-in probe of same-origin `llms.txt` links that
  reports broken links and `.md` links answering with HTML; also a
  `check_links` input on the `aio-lint-live` workflow
- `docs/markdown-variants.md`: how to publish Markdown page variants

### Security

- `aio-lint`: homepage signals are extracted by a linear-time scanner
  (`scripts/aio_html.py`) instead of backtracking regular expressions that
  hostile markup could stall
- `aio-lint`: connections are pinned to the validated address (DNS rebinding),
  proxy environment variables are ignored, and a whole-fetch deadline is
  enforced (`scripts/aio_net.py`)
- `aio-lint`: address check now requires globally routable addresses (CGNAT,
  `192.0.0.0/24`, `192.88.99.0/24`, site-local IPv6 are refused)
- `aio-lint`: untrusted evidence is escaped in the Markdown report; an unknown
  response charset falls back to UTF-8
- `aio-lint-live` workflow passes inputs through environment variables instead
  of interpolating them into the shell script; checkouts no longer persist
  the job token
- `aio-lint`: the whole-fetch deadline also covers connecting, at most four
  resolved addresses are tried, stalled response headers are cut off, and an
  oversized number in JSON-LD no longer aborts the audit
- Installers refuse to write through a symlinked `.cursor` or `.cursor/skills`

## 1.0.0 — 2026-07-27

Stable **1.0** public MIT release. Same feature set as `0.1.0`, promoted to a
major version for public positioning (skills suite + `aio-lint` CLI/CI).
Variant C (MCP/hosted) remains deferred.

### Changed

- Version branding and `aio-lint` User-Agent set to `1.0`
- Docs/status mark the suite as the stable 1.0 line

## 0.1.0 — 2026-07-27

First public MIT release of the AIO artifact suite + CLI linter.

### Added

- AIO skill suite: `aio-site-audit`, `generate-llms-txt`, `audit-robots-ai-bots`,
  `draft-json-ld` (templates + installer)
- English standalone prompt (`PROMPT.en.md`)
- Network and prompt-injection guardrails for every website-fetching skill
- Safe installer dry-run, overwrite refusal, forced-update backups, and
  cross-platform installer smoke tests
- GitHub issue / PR templates, `CHANGELOG.md`, synthetic
  `examples/aio-audit-report.md`
- Dump antipattern fixture (`examples/llms-dump-antipattern.txt`) and
  WordPress Rank Math replacement guide (`docs/replace-rank-math-llms.md`)
- `aio-lint` CLI (`scripts/aio_lint.py`) with SSRF-safe https fetch, offline
  fixtures, CI fixture job, and `aio-lint-live` workflow_dispatch
- Explicit compatibility and outcome-limit documentation

### Changed

- Shared dump/curation heuristics extracted to `scripts/aio_heuristics.py`
- Golden `example-llms.txt` now includes verified About/Privacy and suite repo
  links; CI rejects Rank Math-style dumps as the golden sample
- Public GitHub About/topics/homepage wired for discoverability
- Cursor examples now use `/skill-name` invocation
- Bot policy guidance distinguishes training, search, grounding, and
  user-triggered fetchers
- `llms.txt` size and section counts are documented as curation heuristics
- Schema.org validation guidance is separated from Google Rich Results support
- README / AGENTS positioned as experimental artifact suite (no SEO/AI ranking
  promises)

### Security

- Public site content is treated as untrusted data
- Redirect, private-network target, origin, crawl-size, and binary-fetch
  restrictions are documented
- `robots.txt` is explicitly described as policy rather than access control
- `aio-lint` live mode is https-only with public-IP DNS checks
