# Security

To report a vulnerability, use GitHub’s **Report a vulnerability** under the
Security tab, or email for anything sensitive. Details below.

Russian version: [`SECURITY.ru.md`](SECURITY.ru.md).

## What this project does

This repository ships an **AIO skill suite** (Cursor Skills, prompts, `llms.txt`
/ JSON-LD templates) and an optional stdlib CLI `scripts/aio_lint.py`. The
skills themselves do not install server agents and do not pull npm/pip
dependencies.

`scripts/check_package.py` only reads repository files and validates structure.
It does not use the network except for launching aio-lint against **offline
fixtures**.

`scripts/aio_lint.py` **may** use the network in live mode. Limits: `https`
only, port 443, public DNS IPs (no localhost / private / link-local), same-host
redirects, size and timeout caps. Do not pass staging URLs or lint internal
hosts.

## Risks to be aware of

- An agent running a skill/prompt may fetch the user’s public site URLs
  (sitemap, homepage). Do not put staging hosts, tokens, or private admin paths
  into the prompt.
- A public page may contain indirect prompt injection — text disguised as agent
  instructions. Skills must treat site content as untrusted data and never
  execute commands found there.
- A redirect or DNS name may resolve to localhost, a private/link-local IP, or
  an internal service. Re-check the target before every fetch and after every
  redirect; by default the audit stays on the original origin.
- `robots.txt` is a public, voluntarily honored policy, not access control.
  Protect private data with authentication and network controls, not `Disallow`.
- Large sitemaps can cause excessive crawl/context. Workflows bound sampling and
  do not download binaries.
- Templates and examples must not contain credentials.

## How to report an issue

If you find a way for this package’s instructions to trigger dangerous agent
behavior (secret leakage, destructive defaults, URL swapping, etc.):

1. Open the repository **Security** tab → **Report a vulnerability**
   (GitHub Security Advisories).
2. If that is unavailable, email sergey@bezpalov.com with a subject starting
   with `SECURITY:`.

Please **do not open a public issue** for exploitable problems until they are
fixed.

Expected initial response time is a few days. There is no strict SLA.

## What is not a vulnerability

- “The agent drafted an inaccurate `llms.txt`” — prompt/skill quality; open a
  normal issue.
- Stale links in the example — issue / PR.
- `robots.txt` policies the user chose (bot opt-in / opt-out).
- Missing AI-answer or ranking impact: the suite does not guarantee indexing,
  citations, or rankings.

## Supported versions

Fixes ship for the current stable **v1.x** line (`main`). Tag `v0.1.0` remains
in history but is not a separate support branch.
