# Changelog

All notable changes to this project are documented here.

The project uses semantic versioning for public releases. Until the first tag,
changes remain under **Unreleased**.

## Unreleased

Public-release harden landed on `main` (2026-07-27, commit message
`Harden AIO suite for public release`). Ready to cut **v0.1.0** when tagging.

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
- Explicit compatibility and outcome-limit documentation

### Changed

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
