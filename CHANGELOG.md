# Changelog

All notable changes to this project are documented here.

The project uses semantic versioning for public releases. Until the first tag,
changes remain under **Unreleased**.

## Unreleased

### Added

- English standalone prompt (`PROMPT.en.md`)
- Network and prompt-injection guardrails for every website-fetching skill
- Safe installer dry-run, overwrite refusal, forced-update backups, and
  cross-platform installer smoke tests
- Explicit compatibility and outcome-limit documentation

### Changed

- Cursor examples now use `/skill-name` invocation
- Bot policy guidance distinguishes training, search, grounding, and
  user-triggered fetchers
- `llms.txt` size and section counts are documented as curation heuristics
- Schema.org validation guidance is separated from Google Rich Results support

### Security

- Public site content is treated as untrusted data
- Redirect, private-network target, origin, crawl-size, and binary-fetch
  restrictions are documented
- `robots.txt` is explicitly described as policy rather than access control
