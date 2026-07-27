# llms-generator — артефакт для AI-агентов

Пакет для Cursor, Claude, ChatGPT и других агентов: помогает читателю
[статьи про AIO](https://blog.bezpalov.com/optimize-site-for-ai/) быстро
создать или обновить `llms.txt` для своего сайта.

## Состав

| Файл | Назначение |
|------|------------|
| `SKILL.md` | Cursor Agent Skill — пошаговый workflow |
| `PROMPT.md` | Универсальный промпт для любого чата |
| `template-llms.txt` | Пустой шаблон |
| `example-llms.txt` | Живой пример (blog.bezpalov.com) |

## Cursor

```text
# Вариант A — skill в проекте
mkdir .cursor/skills/generate-llms-txt
cp artifacts/llms-generator/SKILL.md .cursor/skills/generate-llms-txt/
# + скопируйте template-llms.txt, example-llms.txt рядом

# Вариант B — один запрос
Откройте PROMPT.md, подставьте URL, вставьте в чат.
```

В чате: `@generate-llms-txt создай llms.txt для https://my-site.com`

## Claude / ChatGPT

1. Откройте `PROMPT.md`
2. Замените `{{URL}}`, тип сайта, язык, аудиторию
3. Вставьте в новый чат
4. Сохраните вывод как `llms.txt` и выложите в корень сайта

## После генерации

1. Проверьте `https://your-site.com/llms.txt` в браузере
2. Добавьте комментарий в `robots.txt` (см. вывод агента)
3. Обновляйте `Last updated` при изменении структуры сайта

## Источник

Sergey Bezpalov — [Как оптимизировать сайт и блог под AI](https://blog.bezpalov.com/optimize-site-for-ai/)
