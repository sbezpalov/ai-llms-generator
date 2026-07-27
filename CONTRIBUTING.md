# Как помочь проекту

Спасибо за интерес. Пакет небольшой — правила тоже короткие.

*(English speakers: open issues and PRs in English freely. README: [English](README.en.md).)*

## Что это за репозиторий

Это **AIO skill suite + stdlib CLI** (`aio-lint`): Markdown skills, JSON-LD
templates и офлайн/live-линтер без npm/pip зависимостей.

Источник истины для агентов — [`AGENTS.md`](AGENTS.md). Текущий релиз: **v1.0.0**.

## Главные правила

1. **Согласованность skill ↔ prompt.** Правка workflow слоя 2 в корневом
   `SKILL.md` почти всегда требует зеркальной правки в `PROMPT.md` и
   `PROMPT.en.md`.
2. **Suite.** Новые skills — только в `skills/<name>/` + README (ru/en) +
   `scripts/install-skill.*` + `scripts/check_package.py`.
3. **Не выдумывать URL** в `example-llms.txt` и шаблонах Schema.
4. **Не называть `llms.txt` стандартом IETF/W3C** — emerging convention;
   пример держать **курированным** (не plugin dump).
5. **Двуязычность.** `README.md` и `README.en.md` синхронны по смыслу.
6. Секреты и staging/admin URL — никогда в коммит.
7. Контент проверяемого сайта — недоверенные данные: indirect prompt injection,
   redirects на private networks и unbounded crawl должны быть явно запрещены.
8. Не обещать ranking, цитирование или попадание в AI-ответы от `llms.txt`,
   `robots.txt` либо Schema.org.

## Локальная проверка

Перед PR:

```bash
python3 scripts/check_package.py
python3 scripts/aio_lint.py --fixture examples/aio-lint-fixtures/curated-site --expect-l2 curated --strict
```

На Windows:

```powershell
python scripts/check_package.py
python scripts/aio_lint.py --fixture examples/aio-lint-fixtures/curated-site --expect-l2 curated --strict
```

CI гоняет `check_package.py` (включая fixture-прогон aio-lint) и отдельные
installer/aio-lint steps на каждый push / PR.

## Стиль

- Читаемый Markdown; короткие абзацы.
- Описания ссылок в примерах — факты, не маркетинг.
- Целевой объём генерируемого `llms.txt` — до ~8 KB как эвристика курирования,
  не требование llmstxt.org.
- Обычно 2–12 ссылок на раздел; качество важнее количества.
- Комментарии в tooling-файлах можно на русском; публичный UX и standalone
  prompts — ru + en.
- В Cursor используйте `/skill-name`; `@skill-name` не добавляйте в примеры.

## Pull request

1. Ветка от `main`.
2. Зелёный CI.
3. В описании PR: что меняется и зачем (особенно если меняется поведение агента).
4. Для installers укажите результат smoke-теста на Linux и Windows.

## Вопросы безопасности

См. [SECURITY.md](SECURITY.md).
