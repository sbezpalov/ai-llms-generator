# Промпт: сгенерировать llms.txt для сайта

Скопируйте блок ниже в **Cursor**, **Claude**, **ChatGPT** или другой агент.
Подставьте свои значения вместо `{{...}}`.

Для полного AIO-аудита (robots + llms.txt + Schema) см. skill `aio-site-audit`
в `skills/aio-site-audit/`.

---

```
Ты помогаешь подготовить curated llms.txt — краткую карту сайта для AI-ботов и LLM
(emerging convention по llmstxt.org, не официальный стандарт W3C/IETF).
Это НЕ dump всех URL из sitemap и НЕ автосписок SEO-плагина.

Сайт: {{URL}}          (только публичный https://, без staging/auth)
Тип: {{blog | corporate | docs | e-commerce | knowledge base}}
Язык контента: {{ru | en | ...}}
Аудитория: {{одно предложение — кто читает и зачем}}

## Задача

1. Изучи структуру сайта:
   - sitemap.xml / sitemap_index.xml (для навигации по разделам, не для полного дампа)
   - главная страница, навигация, footer
   - существующие robots.txt и llms.txt (если llms.txt — bulk dump, предложи curated замену)

2. Составь файл llms.txt в формате llmstxt.org:

# Название сайта

> Краткий слоган или описание

2–4 предложения: что за сайт, для кого, основные темы, кто автор/компания.

Last updated: YYYY-MM-DD

## Раздел

- [Заголовок страницы](https://полный-url/): описание в одну строку до 160 символов.

## Optional

- [Вторичная страница](https://полный-url/): то, что можно пропустить при нехватке контекста.

3. Правила:
   - 5–12 ссылок на раздел, только проверенные абсолютные URL
   - приоритет: evergreen, About, Contact, ключевые материалы
   - для docs: если есть twin `.md` / `index.html.md` — предпочитай их
   - исключить: логин, корзина, поиск, пагинация, staging
   - язык — как на сайте; без маркетинговой воды
   - объём до ~8 KB

4. Дай фрагмент-комментарий для robots.txt (это НЕ директива для ботов;
   discovery = файл https://{{host}}/llms.txt в корне):

# LLM-oriented site map (human/editor note — not a crawler directive)
# https://{{host}}/llms.txt

5. Кратко: как выложить llms.txt в корень сайта для моего стека
   ({{WordPress | static | Vercel | другое}}).

6. Чек-лист из 5 пунктов: что проверить после публикации.

Не выдумывай URL. Если страницу не удалось проверить — пометь TODO.
Политику AI user-agent (GPTBot и т.д.) не добавляй, пока пользователь явно не попросит.
```

---

## Пример заполнения

```
Сайт: https://docs.example.com
Тип: docs
Язык контента: en
Аудитория: backend developers integrating our payments API
```

## Cursor

Скопируйте skill в `.cursor/skills/generate-llms-txt/` (файлы `SKILL.md`,
`PROMPT.md`, `template-llms.txt`, `example-llms.txt`) или:

```bash
./scripts/install-skill.sh /path/to/project
```

В чате: `@generate-llms-txt создай llms.txt для https://my-site.com`

## English version

Replace the task section language with English if the site is English-first;
the output format stays the same.
