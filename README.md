# ai-llms-generator

[![CI](https://github.com/sbezpalov/ai-llms-generator/actions/workflows/ci.yml/badge.svg)](https://github.com/sbezpalov/ai-llms-generator/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**Русский** · [English](README.en.md)

Экспериментальный набор skills для аудита AIO-артефактов в Cursor и других
агентах: проверяет политику AI-краулеров в `robots.txt`, готовит
**курированный** [`llms.txt`](https://llmstxt.org/) и черновики фактического
Schema.org JSON-LD.

> `llms.txt` — **emerging convention**, не IETF/W3C-стандарт.
> Курированная карта ≠ dump всех URL из SEO-плагина.

Suite не гарантирует индексацию, цитирование, попадание в AI-ответы или рост
позиций. Поддержка `llms.txt` зависит от продукта; Google Search
[не использует его](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)
для Search и generative AI features. `robots.txt` — добровольно соблюдаемая
политика, а Schema.org не гарантирует rich result.

Исходный контекст:
[Как оптимизировать сайт и блог под AI](https://blog.bezpalov.com/optimize-site-for-ai/).
Актуальные ограничения и проверяемые обещания продукта зафиксированы в этом
README и skills.

## Skills (suite)

| Skill | Слой | Когда вызывать |
|-------|------|----------------|
| [`aio-site-audit`](skills/aio-site-audit/SKILL.md) | 0–3 оркестратор | Сводный аудит артефактов |
| [`generate-llms-txt`](SKILL.md) | 2 llms.txt | Создать/обновить курированный индекс |
| [`audit-robots-ai-bots`](skills/audit-robots-ai-bots/SKILL.md) | 1 robots | Политика GPTBot / ClaudeBot / … |
| [`draft-json-ld`](skills/draft-json-ld/SKILL.md) | 3 Schema | Черновики JSON-LD |

Также: [`PROMPT.md`](PROMPT.md) / [`PROMPT.en.md`](PROMPT.en.md) (чат без
Cursor), [`template-llms.txt`](template-llms.txt), [`example-llms.txt`](example-llms.txt)
(golden curated sample для blog.bezpalov.com).
Формат полного отчёта: [`examples/aio-audit-report.md`](examples/aio-audit-report.md).
Антипаттерн dump: [`examples/llms-dump-antipattern.txt`](examples/llms-dump-antipattern.txt).

Репозиторий: [github.com/sbezpalov/ai-llms-generator](https://github.com/sbezpalov/ai-llms-generator).

## Curated vs dump

SEO-плагины (например Rank Math) часто отдают `/llms.txt` как длинный список
всех постов. Это **не** слой 2 AIO. Курированный эталон — `example-llms.txt`.
Как заменить dump на WordPress: [`docs/replace-rank-math-llms.md`](docs/replace-rank-math-llms.md).

## Совместимость

| Среда | Использование |
|-------|---------------|
| Cursor Agent Skills | Нативно из `.cursor/skills/`; явный запуск через `/skill-name` |
| Другие Agent Skills-совместимые агенты | Скопировать каталог skill в поддерживаемый ими skills path |
| Claude / ChatGPT и другие чаты | Использовать `PROMPT.md` / `PROMPT.en.md` либо вставить нужный `SKILL.md` |

## Установка в Cursor

```bash
./scripts/install-skill.sh /path/to/your-project
# Windows: .\scripts\install-skill.ps1 -Target C:\path\to\your-project
```

Скопирует suite в `.cursor/skills/{generate-llms-txt,audit-robots-ai-bots,draft-json-ld,aio-site-audit}/`.
Если skill уже существует, установщик остановится без перезаписи. Для
осознанного обновления с резервной копией используйте `--force` или `-Force`;
для просмотра плана — `--dry-run` или `-DryRun`.

В чате:

```text
/aio-site-audit проверь https://my-site.com
/generate-llms-txt создай llms.txt для https://my-site.com
```

## Claude / ChatGPT

1. Для одного слоя llms.txt — [`PROMPT.md`](PROMPT.md) или
   [`PROMPT.en.md`](PROMPT.en.md)
2. Для аудита / Schema / robots — откройте соответствующий `skills/*/SKILL.md` и вставьте workflow в чат

## После генерации

1. `https://your-site.com/llms.txt` открывается в браузере
2. Комментарий в `robots.txt` — напоминание редактору, **не** директива бота
3. JSON-LD проверьте в Schema Markup Validator; Rich Results Test применим
   только к поддерживаемым Google типам
4. Обновляйте `Last updated` при смене структуры
5. Вручную подтвердите URL и факты перед публикацией

## Контрибьюторам

Каркас [ai-tooling-starter-kit](https://github.com/sbezpalov/ai-tooling-starter-kit),
источник истины — [`AGENTS.md`](AGENTS.md). См. [CONTRIBUTING.md](CONTRIBUTING.md),
[SECURITY.md](SECURITY.md).

```bash
python scripts/check_package.py
```

История изменений: [CHANGELOG.md](CHANGELOG.md).

## Лицензия

[MIT](LICENSE) © 2026 Sergey Bezpalov
