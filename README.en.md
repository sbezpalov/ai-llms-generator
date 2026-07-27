# ai-llms-generator

[![CI](https://github.com/sbezpalov/ai-llms-generator/actions/workflows/ci.yml/badge.svg)](https://github.com/sbezpalov/ai-llms-generator/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

[Русский](README.md) · **English**

An AIO skill suite for Cursor and other agents: **three layers** — `robots.txt`
(AI bot policy), a **curated** [`llms.txt`](https://llmstxt.org/), and Schema.org
JSON-LD — so both people and LLMs can understand a site.

> `llms.txt` is an **emerging convention**, not an IETF/W3C standard.
> A curated map is not a dump of every URL from an SEO plugin.

Background: [How to optimize a site and blog for AI](https://blog.bezpalov.com/optimize-site-for-ai/)
(article in Russian; skills work in the site’s primary language).

## Skills (suite)

| Skill | Layer | When to use |
|-------|-------|-------------|
| [`aio-site-audit`](skills/aio-site-audit/SKILL.md) | 0–3 orchestrator | Full AIO audit |
| [`generate-llms-txt`](SKILL.md) | 2 llms.txt | Create/update curated index |
| [`audit-robots-ai-bots`](skills/audit-robots-ai-bots/SKILL.md) | 1 robots | GPTBot / ClaudeBot / … policy |
| [`draft-json-ld`](skills/draft-json-ld/SKILL.md) | 3 Schema | JSON-LD drafts |

Also: [`PROMPT.md`](PROMPT.md) (any chat UI), [`template-llms.txt`](template-llms.txt),
[`example-llms.txt`](example-llms.txt) (golden curated sample).

## Install in Cursor

```bash
./scripts/install-skill.sh /path/to/your-project
# Windows: .\scripts\install-skill.ps1 -Target C:\path\to\your-project
```

Copies the suite into `.cursor/skills/{generate-llms-txt,audit-robots-ai-bots,draft-json-ld,aio-site-audit}/`.

In chat:

```text
@aio-site-audit audit https://my-site.com
@generate-llms-txt create llms.txt for https://my-site.com
```

## Claude / ChatGPT

1. For llms.txt alone — use [`PROMPT.md`](PROMPT.md)
2. For audit / Schema / robots — paste the workflow from the matching `skills/*/SKILL.md`

## After generation

1. Open `https://your-site.com/llms.txt` in a browser
2. A `robots.txt` comment is an **editor note**, not a crawler directive
3. Validate JSON-LD with Rich Results / a schema validator
4. Bump `Last updated` when the site structure changes

## Contributors

Scaffolded with [ai-tooling-starter-kit](https://github.com/sbezpalov/ai-tooling-starter-kit);
source of truth is [`AGENTS.md`](AGENTS.md). See [CONTRIBUTING.md](CONTRIBUTING.md),
[SECURITY.md](SECURITY.md).

```bash
python scripts/check_package.py
```

## License

[MIT](LICENSE) © 2026 Sergey Bezpalov
