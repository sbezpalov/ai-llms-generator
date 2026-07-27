# ai-llms-generator

[![CI](https://github.com/sbezpalov/ai-llms-generator/actions/workflows/ci.yml/badge.svg)](https://github.com/sbezpalov/ai-llms-generator/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

[Русский](README.md) · **English**

A package for Cursor, Claude, ChatGPT, and other agents: quickly create or update
[`llms.txt`](https://blog.bezpalov.com/optimize-site-for-ai/) — a short human- and
LLM-readable site index — plus a `robots.txt` comment snippet.

> `llms.txt` is an **emerging convention**, not an IETF/W3C standard.

## Contents

| File | Purpose |
|------|---------|
| [`SKILL.md`](SKILL.md) | Cursor Agent Skill — step-by-step workflow |
| [`PROMPT.md`](PROMPT.md) | Drop-in prompt for any chat UI |
| [`template-llms.txt`](template-llms.txt) | Empty template |
| [`example-llms.txt`](example-llms.txt) | Live example (blog.bezpalov.com) |
| [`AGENTS.md`](AGENTS.md) | Project context for AI tooling |
| [`scripts/`](scripts/) | Skill installer + CI smoke checks |

## Install in Cursor

Copy the skill into your project (or Cursor’s global skills folder):

```bash
mkdir -p .cursor/skills/generate-llms-txt
cp SKILL.md PROMPT.md template-llms.txt example-llms.txt .cursor/skills/generate-llms-txt/
```

Or from a clone of this repository:

```bash
./scripts/install-skill.sh /path/to/your-project
# Windows: .\scripts\install-skill.ps1 -Target C:\path\to\your-project
```

In chat:

```text
@generate-llms-txt create llms.txt for https://my-site.com
```

Or skip the skill: open `PROMPT.md`, fill in the URL, paste into a chat.

## Claude / ChatGPT

1. Open [`PROMPT.md`](PROMPT.md)
2. Replace `{{URL}}`, site type, language, audience
3. Paste into a new chat
4. Save the output as `llms.txt` at the site root

## After generation

1. Open `https://your-site.com/llms.txt` in a browser
2. Paste the suggested comment into `robots.txt`
3. Bump `Last updated` when the site structure changes

## Contributors & agents

Scaffolded with the [ai-tooling-starter-kit](https://github.com/sbezpalov/ai-tooling-starter-kit)
model (`AGENTS.md` as source of truth). See [CONTRIBUTING.md](CONTRIBUTING.md) and
[SECURITY.md](SECURITY.md).

## Background

Sergey Bezpalov — [How to optimize a site and blog for AI](https://blog.bezpalov.com/optimize-site-for-ai/)
(article in Russian; the skill/prompt work in English or the site’s primary language).

## License

[MIT](LICENSE) © 2026 Sergey Bezpalov
