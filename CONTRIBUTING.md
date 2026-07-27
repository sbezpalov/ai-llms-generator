# Как помочь проекту

Спасибо за интерес. Пакет небольшой — правила тоже короткие.

*(English speakers: open issues and PRs in English freely. README: [English](README.en.md).)*

## Что это за репозиторий

Это **AIO skill suite** (Markdown skills + JSON-LD templates), не приложение.
Рантайма и зависимостей npm/pip нет.

Источник истины для агентов — [`AGENTS.md`](AGENTS.md).

## Главные правила

1. **Согласованность skill ↔ prompt.** Правка workflow слоя 2 в корневом
   `SKILL.md` почти всегда требует зеркальной правки в `PROMPT.md`.
2. **Suite.** Новые skills — только в `skills/<name>/` + README (ru/en) +
   `scripts/install-skill.*` + `scripts/check_package.py`.
3. **Не выдумывать URL** в `example-llms.txt` и шаблонах Schema.
4. **Не называть `llms.txt` стандартом IETF/W3C** — emerging convention;
   пример держать **курированным** (не plugin dump).
5. **Двуязычность.** `README.md` и `README.en.md` синхронны по смыслу.
6. Секреты и staging/admin URL — никогда в коммит.

## Локальная проверка

Перед PR:

```bash
python3 scripts/check_package.py
```

На Windows:

```powershell
python scripts/check_package.py
```

CI гоняет тот же скрипт на каждый push / PR.

## Стиль

- Читаемый Markdown; короткие абзацы.
- Описания ссылок в примерах — факты, не маркетинг.
- Целевой объём генерируемого `llms.txt` — до ~8 KB.
- Комментарии в tooling-файлах можно на русском; публичный UX — ru + en.

## Pull request

1. Ветка от `main`.
2. Зелёный CI.
3. В описании PR: что меняется и зачем (особенно если меняется поведение агента).

## Вопросы безопасности

См. [SECURITY.md](SECURITY.md).
