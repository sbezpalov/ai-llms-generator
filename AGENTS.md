# AGENTS.md — ai-llms-generator

> **Источник истины для всех AI-инструментов и людей в этом репозитории.**
> Файл читают нативно Cursor, Google Antigravity/Gemini и другие AGENTS-совместимые
> инструменты. Тонкие редиректы (`.cursorrules`, `CLAUDE.md`, `GEMINI.md`,
> `PERPLEXITY.md`) дополняют, но не отменяют эти правила. **Прочитай целиком перед работой.**

## 1. Проект

Публичный MIT-пакет для AI-агентов (Cursor Skill + универсальный промпт): помогает
аудировать сайт и собрать production-ready `llms.txt` плюс фрагмент для `robots.txt`.

Целевая аудитория — владельцы блогов, docs и корпоративных сайтов, которые хотят
сделать контент понятным для LLM/AI-краулеров (AIO). Контекст и мотивация —
[статья про AIO](https://blog.bezpalov.com/optimize-site-for-ai/).

## 2. Стек

- Контент: Markdown / plain text (`SKILL.md`, `PROMPT.md`, шаблоны `*.txt`)
- Cursor Agent Skills (YAML frontmatter в `SKILL.md`)
- AI tooling scaffold v2: `AGENTS.md` + тонкие редиректы (Claude / Cursor / Gemini / Perplexity)
- CI: GitHub Actions (smoke-проверки структуры и frontmatter)
- Лицензия: MIT

Кода приложения, рантайма и зависимостей npm/pip **нет** — это skill/prompt-пакет.

## 3. Структура

| Путь | Назначение |
|------|------------|
| `SKILL.md` | Cursor Agent Skill — пошаговый workflow генерации `llms.txt` |
| `PROMPT.md` | Универсальный промпт для Claude / ChatGPT / любого чата |
| `template-llms.txt` | Пустой шаблон `llms.txt` |
| `example-llms.txt` | Живой пример (blog.bezpalov.com) |
| `AGENTS.md` | ★ контекст и правила для агентов |
| `README.md` / `README.en.md` | Документация (ru / en) |
| `CONTRIBUTING.md` | Как контрибьютить |
| `SECURITY.md` | Политика сообщений о проблемах |
| `LICENSE` | MIT |
| `scripts/check_package.py` | CI smoke-проверки структуры пакета |
| `scripts/install-skill.*` | Установка skill в чужой проект |
| `.cursor/rules/` | Cursor-правила (проект + safety + домен) |
| `.claude/` | Claude Code settings / commands / agents |
| `.ai/` | Карта раскладки + кросс-артефакты |

## 4. Статус / текущий приоритет

Публичный MIT-релиз skill-пакета: каркас AI tooling, двуязычная документация,
CONTRIBUTING/SECURITY, CI smoke. Дальше — обратная связь по качеству генерируемых
`llms.txt` и уточнение workflow под новые конвенции AIO.

## 5. Как вносить изменения (агент)

- Работай через план: декомпозируй задачу и покажи шаги ДО исполнения.
- Human-in-the-loop: для необратимых операций — остановись и спроси.
- Изменения атомарные; объясняй ЧТО и ПОЧЕМУ.
- Правки skill/prompt — проверяй согласованность `SKILL.md` ↔ `PROMPT.md` ↔ шаблоны.
- Не выдумывай URL в примерах; `example-llms.txt` должен отражать реальные страницы
  или быть явно помечен как вымышленный.
- Новый CI/скрипт — зелёный прогон до DoD.

## 6. Безопасность (NEVER)

- Секреты (пароли, ключи, токены, `.env`, локальные конфиги) — не коммитить и не выводить.
- Не добавлять в шаблоны/примеры staging hosts, admin paths, credentials.
- Не инструктировать агентов блокировать всех AI-ботов по умолчанию без явного запроса пользователя.
- Не заявлять, что `llms.txt` — официальный стандарт IETF/W3C (это emerging convention).
- Доставка: только через git → публичный GitHub; прод-сайты пользователей не трогать.

## 7. Definition of Done

- [ ] Изменение локально; секреты не попали в код/коммит.
- [ ] `SKILL.md` / `PROMPT.md` / шаблоны согласованы; CI smoke зелёный.
- [ ] README.ru и README.en отражают поведение (если менялся UX установки).
- [ ] Diff отревьюен; есть краткий план отката (revert commit).

## Раскладка инструментов

Артефакты — в `.ai/artifacts/` (кросс) и `.<инструмент>/artifacts/`. Детали — `.ai/README.md`.

<!-- Инициализировано init-ai-tooling v2 (2026-07-27); заполнено под публичный MIT-релиз. -->
