# AGENTS.md — ai-llms-generator

> **Источник истины для всех AI-инструментов и людей в этом репозитории.**
> Файл читают нативно Cursor, Google Antigravity/Gemini и другие AGENTS-совместимые
> инструменты. Тонкие редиректы (`.cursorrules`, `CLAUDE.md`, `GEMINI.md`,
> `PERPLEXITY.md`) дополняют, но не отменяют эти правила. **Прочитай целиком перед работой.**

## 1. Проект

Публичный MIT **AIO skill suite** для AI-агентов: три слоя оптимизации сайта под
LLM — политика AI-ботов в `robots.txt`, **курированный** `llms.txt` (emerging
convention, llmstxt.org), Schema.org JSON-LD. Оркестратор — `aio-site-audit`.

Целевая аудитория — владельцы блогов, docs и корпоративных сайтов (AIO).
Контекст: [статья про AIO](https://blog.bezpalov.com/optimize-site-for-ai/).

## 2. Стек

- Контент: Markdown skills + JSON-LD templates (без npm/pip рантайма продукта)
- Cursor Agent Skills (YAML frontmatter)
- AI tooling scaffold v2: `AGENTS.md` + редиректы
- CI: `scripts/check_package.py` (структура, frontmatter, формат llms.txt, JSON)
- Лицензия: MIT

## 3. Структура

| Путь | Назначение |
|------|------------|
| `SKILL.md` + `PROMPT.md` + `template-llms.txt` + `example-llms.txt` | Skill **generate-llms-txt** (слой 2; root = BC для блога/zip) |
| `skills/aio-site-audit/` | Оркестратор трёх слоёв |
| `skills/audit-robots-ai-bots/` | Слой 1 — AI bots / robots.txt |
| `skills/draft-json-ld/` | Слой 3 — Schema.org + `templates/*.json` |
| `scripts/install-skill.*` | Установка всего suite в `.cursor/skills/` |
| `scripts/check_package.py` | CI smoke |
| `AGENTS.md` | ★ контекст агентов |
| `README.md` / `README.en.md` | Документация |
| `CONTRIBUTING.md` / `SECURITY.md` / `LICENSE` | OSS |

## 4. Статус / текущий приоритет

Вариант A: multi-skill AIO suite + Wave 0 (spec llmstxt.org, curated vs dump,
robots-comment truth). Дальше по спросу — CLI linter (вариант B).

## 5. Как вносить изменения (агент)

- План до исполнения; human-in-the-loop для необратимого.
- Согласованность: правки слоя 2 — `SKILL.md` ↔ `PROMPT.md` ↔ шаблоны.
- Новые skills — каталог `skills/<name>/SKILL.md` + запись в README ru/en,
  `install-skill.*`, `check_package.py`.
- Example = **curated golden**; не копировать Rank Math / plugin dumps.
- Не выдумывать URL и Schema-факты (рейтинги, телефоны).

## 6. Безопасность (NEVER)

- Секреты не коммитить и не выводить.
- Только публичный `https`; без staging/admin/auth headers.
- Не блокировать всех AI-ботов по умолчанию без явного запроса пользователя.
- Не называть `llms.txt` стандартом IETF/W3C (emerging convention).
- Не утверждать, что комментарий в `robots.txt` — директива discovery для ботов.
- Прод-сайты пользователей не менять без подтверждения.

## 7. Definition of Done

- [ ] Секреты не в коммите; только локальные правки.
- [ ] `python scripts/check_package.py` зелёный; README.ru ↔ README.en синхронны по смыслу.
- [ ] Skills согласованы с оркестратором `aio-site-audit`.
- [ ] Diff отревьюен; откат = revert commit.

## Раскладка инструментов

Артефакты — в `.ai/artifacts/` и `.<инструмент>/artifacts/`. Детали — `.ai/README.md`.

<!-- Инициализировано init-ai-tooling v2 (2026-07-27); AIO suite variant A. -->
