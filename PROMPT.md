# Промпт: сгенерировать llms.txt для сайта

Скопируйте блок ниже в **Cursor**, **Claude**, **ChatGPT** или другой агент.
Подставьте свои значения вместо `{{...}}`.

---

```
Ты помогаешь подготовить llms.txt — краткую карту сайта для AI-ботов и LLM
(emerging convention, не официальный стандарт W3C).

Сайт: {{URL}}          (например https://example.com)
Тип: {{blog | corporate | docs | e-commerce | knowledge base}}
Язык контента: {{ru | en | ...}}
Аудитория: {{одно предложение — кто читает и зачем}}

## Задача

1. Изучи структуру сайта:
   - sitemap.xml / sitemap_index.xml
   - главная страница, навигация, footer
   - существующие robots.txt и llms.txt (если есть)

2. Составь файл llms.txt в формате:

# Название сайта

> Краткий слоган или описание

2–4 предложения: что за сайт, для кого, основные темы, кто автор/компания.

Last updated: YYYY-MM-DD

## Раздел

- [Заголовок страницы](https://полный-url/): описание в одну строку до 160 символов.

3. Правила:
   - 5–12 ссылок на раздел, только проверенные абсолютные URL
   - приоритет: evergreen-страницы, About, Contact, ключевые материалы
   - исключить: логин, корзина, поиск, пагинация, staging
   - язык — как на сайте; без маркетинговой воды
   - объём до ~8 KB

4. Дай фрагмент для robots.txt:

# LLM site map (human/LLM-readable index)
# https://{{host}}/llms.txt

5. Кратко: как выложить llms.txt в корень сайта для моего стека
   ({{WordPress | static | Vercel | другое}}).

6. Чек-лист из 5 пунктов: что проверить после публикации.

Не выдумывай URL. Если страницу не удалось проверить — пометь TODO.
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

Положите папку `llms-generator` в `.cursor/skills/` проекта или вызовите
`@generate-llms-txt` после копирования `SKILL.md` в skills.

## English version

Replace the task section language with English if the site is English-first;
the output format stays the same.
