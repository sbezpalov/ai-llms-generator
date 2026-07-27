# ai-llms-generator

[![CI](https://github.com/sbezpalov/ai-llms-generator/actions/workflows/ci.yml/badge.svg)](https://github.com/sbezpalov/ai-llms-generator/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**Русский** · [English](README.en.md)

AIO-набор для Cursor и других агентов: **три слоя** — `robots.txt` (политика
AI-ботов), **курированный** [`llms.txt`](https://llmstxt.org/) и Schema.org
JSON-LD — чтобы сайт понимали и люди, и LLM.

> `llms.txt` — **emerging convention**, не IETF/W3C-стандарт.
> Курированная карта ≠ dump всех URL из SEO-плагина.

Контекст: [Как оптимизировать сайт и блог под AI](https://blog.bezpalov.com/optimize-site-for-ai/).

## Skills (suite)

| Skill | Слой | Когда вызывать |
|-------|------|----------------|
| [`aio-site-audit`](skills/aio-site-audit/SKILL.md) | 0–3 оркестратор | Полный AIO-аудит |
| [`generate-llms-txt`](SKILL.md) | 2 llms.txt | Создать/обновить курированный индекс |
| [`audit-robots-ai-bots`](skills/audit-robots-ai-bots/SKILL.md) | 1 robots | Политика GPTBot / ClaudeBot / … |
| [`draft-json-ld`](skills/draft-json-ld/SKILL.md) | 3 Schema | Черновики JSON-LD |

Также: [`PROMPT.md`](PROMPT.md) (чат без Cursor), [`template-llms.txt`](template-llms.txt),
[`example-llms.txt`](example-llms.txt) (golden curated sample).

## Установка в Cursor

```bash
./scripts/install-skill.sh /path/to/your-project
# Windows: .\scripts\install-skill.ps1 -Target C:\path\to\your-project
```

Скопирует suite в `.cursor/skills/{generate-llms-txt,audit-robots-ai-bots,draft-json-ld,aio-site-audit}/`.

В чате:

```text
@aio-site-audit проверь https://my-site.com
@generate-llms-txt создай llms.txt для https://my-site.com
```

## Claude / ChatGPT

1. Для одного слоя llms.txt — [`PROMPT.md`](PROMPT.md)
2. Для аудита / Schema / robots — откройте соответствующий `skills/*/SKILL.md` и вставьте workflow в чат

## После генерации

1. `https://your-site.com/llms.txt` открывается в браузере
2. Комментарий в `robots.txt` — напоминание редактору, **не** директива бота
3. JSON-LD проверьте в Rich Results / schema validator
4. Обновляйте `Last updated` при смене структуры

## Контрибьюторам

Каркас [ai-tooling-starter-kit](https://github.com/sbezpalov/ai-tooling-starter-kit),
источник истины — [`AGENTS.md`](AGENTS.md). См. [CONTRIBUTING.md](CONTRIBUTING.md),
[SECURITY.md](SECURITY.md).

```bash
python scripts/check_package.py
```

## Лицензия

[MIT](LICENSE) © 2026 Sergey Bezpalov
