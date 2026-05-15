# CLAUDE.md — Руководство по работе с проектом

## Что это за проект

Личный блог **sergeypruss.ru** — полностью статический сайт на GitHub Pages без фреймворков. ~155 постов на русском языке о бизнесе, лидерстве, саморазвитии. Не используется Jekyll, Hugo или Eleventy — кастомный Python-генератор.

## Архитектура

```
posts.js          ← единственный источник метаданных о постах
generate.py       ← пересобирает blog.html, blog/page-N.html, feed.xml, tag-*.html
posts/*.html      ← готовые HTML-файлы постов (НЕ markdown)
components.js     ← runtime-инъекция header/footer/author-block через fetch()
styles/site.css   ← основные стили, CSS-переменные (--ink, --accent, --line)
```

**Данные текут так:** `posts.js` → `python3 generate.py` → статические HTML-файлы → git push → GitHub Pages.

## Как добавить новый пост

1. Создать `posts/<slug>.html` — готовый HTML-файл поста (см. структуру ниже).
2. Добавить запись в начало массива `POSTS` в `posts.js`:
   ```js
   {slug:`transliterated-slug`, date:`12 May 2026`, title:`Заголовок`, description:`Краткое описание...`}
   ```
3. Запустить `python3 generate.py` — пересоберёт индекс, пагинацию, RSS, теги.
4. Закоммитить всё: `posts/<slug>.html`, `posts.js`, и все сгенерированные файлы.

## Структура HTML-файла поста

```html
<!DOCTYPE html>
<html lang="ru">
<head>
  <!-- meta charset, viewport, canonical, title, description -->
  <!-- og: теги (og:title, og:description, og:image, og:url, og:type) -->
  <!-- article:published_time в ISO формате -->
  <!-- JSON-LD: Article + BreadcrumbList -->
  <!-- CSS с cache-buster: styles/site.css?v=15 -->
</head>
<body>
  <div id="site-header"></div>          <!-- инъектируется components.js -->

  <article class="post">
    <div class="post-header">
      <time>12 мая 2026</time>
      <h1>Заголовок поста</h1>
    </div>
    <div class="post-body">
      <!-- HTML-параграфы с тегами <p>, <ul>, <blockquote>, <a> -->
    </div>
  </article>

  <nav class="post-nav">
    <!-- ссылки на пред./след. пост — генерируются generate.py -->
  </nav>

  <div class="post-related-static">
    <!-- 3 рекомендованных поста — генерируются generate.py -->
  </div>

  <div id="site-footer"></div>          <!-- инъектируется components.js -->
  <script src="../components.js"></script>
  <script src="../scripts/analytics.js"></script>
</body>
</html>
```

## Слаги (slugs)

- Транслитерация с русского: `быть-счастливым` → `byt-schastlivym`
- Только строчные буквы, дефисы, без спецсимволов
- URL поста: `https://sergeypruss.ru/posts/<slug>.html`

## Теги

Используется ровно 5 тегов: `#книги`, `#лидерство`, `#ценности`, `#кейсы`, `#подкаст`. Не добавлять новые без явного запроса пользователя. Теги прописываются в JSON-LD и в HTML-разметке поста.

## Процесс деплоя

Деплой = `git push`. GitHub Pages публикует автоматически с ветки `main`. CI/CD не настроен. После каждого изменения в `posts.js` **обязательно** запускать `generate.py`.

HTTP 301 с `/blog` и `/blog.html` на `https://sergeypruss.ru/blog/` Pages из репозитория не отдаёт — при DNS в Cloudflare см. `scripts/cloudflare_301_blog_redirects.txt`.

## Утилиты

| Скрипт | Назначение |
|---|---|
| `generate.py` | Пересборка блога, RSS, тегов, пагинации |
| `typograph.py` | Типографская правка русского текста |
| `telegram_import_mvp.py` | Импорт постов из Telegram-канала |
| `seo/manage_backlinks.py` | Управление обратными ссылками |
| `fix_book_posts.py` | Исправление заголовков книжных постов |

## MCP-интеграции

В `.claude/settings.json` подключены MCP-серверы:
- **Google Search Console** — мониторинг SEO-данных
- **Yandex Webmaster** — данные по ru-трафику
- Ключи в `secrets/` (папка в .gitignore — никогда не коммитить)

## Критически важные правила

- **Никогда не коммитить `secrets/`** и любые файлы с API-ключами.
- **Не трогать шрифты** (`fonts/`) без явного запроса — Museo Sans Cyrl, лицензированные.
- **Не менять cache-buster версии** (`?v=15`) без реального изменения файла.
- **Не добавлять новые CSS-переменные** без понимания дизайн-системы.
- После правки любого поста проверять: canonical URL, og:url, JSON-LD url — все три должны совпадать и быть абсолютными (`https://sergeypruss.ru/...`).
- **Ссылки в постах** — только в `<div class="post-body">`, не в `<meta>` и не в JSON-LD.

## SEO-требования для каждого поста

- `<link rel="canonical">` — абсолютный URL
- `og:image` — абсолютный URL картинки (желательно из `img/posts/`)
- `article:published_time` — ISO 8601 (`2026-05-12T00:00:00+03:00`)
- JSON-LD тип `Article` с полями: `headline`, `datePublished`, `author`, `url`, `image`
- JSON-LD тип `BreadcrumbList`: Главная → Блог → Пост

## Типичные задачи и как их решать

**Добавить пост:** создать HTML → обновить posts.js → запустить generate.py → закоммитить.

**Исправить опечатку в посте:** отредактировать `posts/<slug>.html` напрямую. generate.py трогать не нужно.

**Исправить метаданные поста:** обновить `posts.js` (description/title) → запустить generate.py (обновятся карточки в индексе и RSS).

**Добавить картинку к посту:** положить в `img/posts/`, прописать в `og:image` и JSON-LD `image`.

**Проверить сборку:** `python3 generate.py` — должен завершиться без ошибок и вывести список затронутых файлов.
