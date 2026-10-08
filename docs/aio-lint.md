# aio-lint (v1.0)

Stdlib-only CLI that scores AIO artifacts for a **public https** site (or an
offline fixture). Ships in **ai-llms-generator v1.0.0**.

| Layer | Check |
|-------|--------|
| L0 | Homepage title / H1 / canonical / meta description |
| L1 | `robots.txt` reachability, absolute `Sitemap:`, AI user-agent hints |
| L2 | `/llms.txt` missing / unavailable / empty / malformed / dump / curated |
| L3 | Homepage `application/ld+json` `@type` presence |

It does **not** promise rankings, citations, or AI-answer inclusion. Fetched
HTML/text is untrusted data. SSRF controls: https-only, port 443, globally
routable addresses only, connections pinned to the validated address (no DNS
rebinding), same-host redirects re-validated per hop, proxy environment
ignored, size + per-socket + whole-fetch time limits. Page signals are
extracted by a linear-time scanner, and evidence is escaped in the Markdown
report. See [SECURITY.md](../SECURITY.md) for known limitations.

L2 also reports `markdown_links`: how many links point to `.md` page variants,
which the llmstxt.org proposal suggests where a site publishes them. It is
informational only — it never changes the L2 status, and the linter does not
fetch the linked pages unless `--check-links` is given.

## Usage

```bash
# Live site (network)
python scripts/aio_lint.py https://example.com
python scripts/aio_lint.py https://example.com --json --strict
python scripts/aio_lint.py https://example.com --check-links

# Offline fixtures (CI)
python scripts/aio_lint.py --fixture examples/aio-lint-fixtures/curated-site --expect-l2 curated
python scripts/aio_lint.py --fixture examples/aio-lint-fixtures/dump-site --expect-l2 dump
```

Exit codes: `0` success / expected classification, `1` lint or expect mismatch,
`2` usage or refused unsafe URL. Without `--strict` a report with failing
layers still exits `0`.

Status notes:

- **L1** follows RFC 9309: a `4xx` robots.txt means "no policy, crawlers treat
  it as allow-all" (`weak`); a `5xx` means crawlers must assume a complete
  disallow (`fail`). Trailing `#` comments are ignored and only absolute
  `Sitemap:` URLs count.
- **L2** never classifies an error page: `404`/`410` is `missing` (`fail`),
  any other non-200 is `unavailable` (`weak` — a 403 often just means the
  linter was blocked). Link entries are recognised with `-`, `*` or `+`
  bullets; the 20-link / 12-per-section / 8 KB thresholds are project
  heuristics, not llmstxt.org rules.
- **`--check-links`** (live mode, opt-in) fetches up to 25 same-origin links
  from `llms.txt` and reports the ones that do not answer `200`, plus `.md`
  links that answer with an HTML page (soft 404). Problems lower a `curated`
  file to `weak`. Links to other hosts are counted but never fetched. It adds
  one request per link, so expect a longer run. How to publish the variants:
  [markdown-variants.md](markdown-variants.md).
- The target may be an origin or any URL on it; only the origin is audited.
  Credentials and non-default ports are refused rather than dropped.

`CERTIFICATE_VERIFY_FAILED` on every layer means the local Python has no CA
bundle (common with python.org builds on macOS): run that install's
`Install Certificates.command`, or set `SSL_CERT_FILE` to a CA bundle.

## Tests

```bash
python -m unittest discover -s tests -t .
```

Offline: DNS and connections are faked; no request leaves the machine.

## GitHub Actions

Package CI runs fixture mode on every push. For a live URL, use workflow
`aio-lint-live` (`workflow_dispatch` input `url`).
