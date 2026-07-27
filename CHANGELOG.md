# Changelog

All notable changes to this project are documented here.

The project uses semantic versioning for public releases.

## Unreleased

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
