# ai-llms-generator

[![CI](https://github.com/sbezpalov/ai-llms-generator/actions/workflows/ci.yml/badge.svg)](https://github.com/sbezpalov/ai-llms-generator/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/sbezpalov/ai-llms-generator)](https://github.com/sbezpalov/ai-llms-generator/releases)

[Русский](README.md) · **English**

A public MIT **AIO artifact suite** (v1.0): Cursor skills plus the stdlib
`aio-lint` CLI to review three site layers — AI crawler policy in `robots.txt`,
a **curated** [`llms.txt`](https://llmstxt.org/), and factual Schema.org JSON-LD
drafts.

> `llms.txt` is an **emerging convention**, not an IETF/W3C standard.
> A curated map is not a dump of every URL from an SEO plugin.

The suite does not guarantee crawling, citations, AI-answer inclusion, or
rankings. Product support for `llms.txt` varies; Google Search
[does not use it](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)
for Search or its generative AI features. `robots.txt` is a voluntary crawler
policy, and Schema.org does not guarantee a rich result.

Background: [How to optimize a site and blog for AI](https://blog.bezpalov.com/optimize-site-for-ai/)
(article in Russian). Current product boundaries are documented in this README
and the skills; generated output follows the site’s primary language.

## Skills (suite)

| Skill | Layer | When to use |
|-------|-------|-------------|
| [`aio-site-audit`](skills/aio-site-audit/SKILL.md) | 0–3 orchestrator | Combined artifact audit |
| [`generate-llms-txt`](SKILL.md) | 2 llms.txt | Create/update curated index |
| [`audit-robots-ai-bots`](skills/audit-robots-ai-bots/SKILL.md) | 1 robots | GPTBot / ClaudeBot / … policy |
| [`draft-json-ld`](skills/draft-json-ld/SKILL.md) | 3 Schema | JSON-LD drafts |

Also: [`PROMPT.en.md`](PROMPT.en.md) / [`PROMPT.md`](PROMPT.md) (any chat UI),
[`template-llms.txt`](template-llms.txt), [`example-llms.txt`](example-llms.txt)
(golden curated sample for blog.bezpalov.com).
Full report format: [`examples/aio-audit-report.md`](examples/aio-audit-report.md).
Dump anti-pattern: [`examples/llms-dump-antipattern.txt`](examples/llms-dump-antipattern.txt).

Three-layer CLI linter (SSRF-safe): [`docs/aio-lint.md`](docs/aio-lint.md)
(`python scripts/aio_lint.py https://example.com`).

Repository: [github.com/sbezpalov/ai-llms-generator](https://github.com/sbezpalov/ai-llms-generator).

## Curated vs dump

SEO plugins (e.g. Rank Math) often expose `/llms.txt` as a long post dump. That
is **not** AIO layer 2. The curated golden is `example-llms.txt`. How to replace
a WordPress dump: [`docs/replace-rank-math-llms.md`](docs/replace-rank-math-llms.md).

## Compatibility

| Environment | Usage |
|-------------|-------|
| Cursor Agent Skills | Native under `.cursor/skills/`; invoke explicitly with `/skill-name` |
| Other Agent Skills-compatible agents | Copy each skill directory into the tool’s supported skills path |
| Claude / ChatGPT and other chat UIs | Use `PROMPT.md` / `PROMPT.en.md`, or paste the relevant `SKILL.md` |

## Install in Cursor

```bash
./scripts/install-skill.sh /path/to/your-project
# Windows: .\scripts\install-skill.ps1 -Target C:\path\to\your-project
```

Copies the suite into `.cursor/skills/{generate-llms-txt,audit-robots-ai-bots,draft-json-ld,aio-site-audit}/`.
If a skill already exists, the installer stops without overwriting it. Use
`--force` or `-Force` for an intentional update with a backup, and `--dry-run`
or `-DryRun` to preview the operation.

In chat:

```text
/aio-site-audit audit https://my-site.com
/generate-llms-txt create llms.txt for https://my-site.com
```

## Claude / ChatGPT

1. For llms.txt alone — use [`PROMPT.en.md`](PROMPT.en.md) or
   [`PROMPT.md`](PROMPT.md)
2. For audit / Schema / robots — paste the workflow from the matching `skills/*/SKILL.md`

## After generation

1. Open `https://your-site.com/llms.txt` in a browser
2. A `robots.txt` comment is an **editor note**, not a crawler directive
3. Validate JSON-LD with Schema Markup Validator; use Rich Results Test only
   for types currently supported by Google
4. Bump `Last updated` when the site structure changes
5. Manually confirm every URL and fact before publishing

## Contributors

Scaffolded with [ai-tooling-starter-kit](https://github.com/sbezpalov/ai-tooling-starter-kit);
source of truth is [`AGENTS.md`](AGENTS.md). See [CONTRIBUTING.md](CONTRIBUTING.md),
[SECURITY.md](SECURITY.md).

```bash
python scripts/check_package.py
python scripts/aio_lint.py --fixture examples/aio-lint-fixtures/curated-site --expect-l2 curated --strict
```

See [CHANGELOG.md](CHANGELOG.md) for changes. Current release: **v1.0.0**.

## License

[MIT](LICENSE) © 2026 Sergey Bezpalov
