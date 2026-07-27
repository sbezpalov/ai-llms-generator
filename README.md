# ai-llms-generator

[![CI](https://github.com/sbezpalov/ai-llms-generator/actions/workflows/ci.yml/badge.svg)](https://github.com/sbezpalov/ai-llms-generator/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**Русский** · [English](README.en.md)

Пакет для Cursor, Claude, ChatGPT и других агентов: помогает быстро создать или
обновить [`llms.txt`](https://blog.bezpalov.com/optimize-site-for-ai/) — краткую
человеко- и LLM-читаемую карту сайта — плюс комментарий для `robots.txt`.

> `llms.txt` — **emerging convention**, не официальный стандарт IETF/W3C.

## Состав

| Файл | Назначение |
|------|------------|
| [`SKILL.md`](SKILL.md) | Cursor Agent Skill — пошаговый workflow |
| [`PROMPT.md`](PROMPT.md) | Универсальный промпт для любого чата |
| [`template-llms.txt`](template-llms.txt) | Пустой шаблон |
| [`example-llms.txt`](example-llms.txt) | Живой пример (blog.bezpalov.com) |
| [`AGENTS.md`](AGENTS.md) | Контекст проекта для AI-инструментов |
| [`scripts/`](scripts/) | Установка skill + CI smoke-проверки |

## Установка в Cursor

Скопируйте skill в проект (или в глобальные skills Cursor):

```bash
mkdir -p .cursor/skills/generate-llms-txt
cp SKILL.md PROMPT.md template-llms.txt example-llms.txt .cursor/skills/generate-llms-txt/
```

Или из клона этого репозитория:

```bash
./scripts/install-skill.sh /path/to/your-project
# Windows: .\scripts\install-skill.ps1 -Target C:\path\to\your-project
```

В чате:

```text
@generate-llms-txt создай llms.txt для https://my-site.com
```

Либо без skill: откройте `PROMPT.md`, подставьте URL и вставьте в чат.

## Claude / ChatGPT

1. Откройте [`PROMPT.md`](PROMPT.md)
2. Замените `{{URL}}`, тип сайта, язык, аудиторию
3. Вставьте в новый чат
4. Сохраните вывод как `llms.txt` в корне сайта

## После генерации

1. Проверьте `https://your-site.com/llms.txt` в браузере
2. Добавьте комментарий в `robots.txt` (агент подскажет фрагмент)
3. Обновляйте `Last updated` при изменении структуры сайта

## Для контрибьюторов и агентов

Репозиторий развёрнут по модели [ai-tooling-starter-kit](https://github.com/sbezpalov/ai-tooling-starter-kit)
(`AGENTS.md` = источник истины). См. [CONTRIBUTING.md](CONTRIBUTING.md) и
[SECURITY.md](SECURITY.md).

## Источник

Sergey Bezpalov — [Как оптимизировать сайт и блог под AI](https://blog.bezpalov.com/optimize-site-for-ai/)

## Лицензия

[MIT](LICENSE) © 2026 Sergey Bezpalov
