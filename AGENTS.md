Это личный статический сайт Сергея Прусса.

Структура проекта:
- Основные страницы: index.html, blog/index.html (главная блога), blog/page-N.html (пагинация)
- Теги: tags/knigi.html, tags/liderstvo.html, tags/tsennosti.html, tags/keysy.html, tags/podkast.html
- Партиалы (загружаются через components.js): _partials/header.html, _partials/footer.html, _partials/author-block.html, _partials/tags-nav.html
- Контент и данные: posts.js, components.js
- Ресурсы: img/, fonts/, files/
- Вспомогательные скрипты: scripts/generate.py, scripts/typograph.py, scripts/fix_book_posts.py, scripts/fix_tags.py, scripts/telegram_import_mvp.py
- blog.html — redirect-заглушка на /blog/ (не редактировать)

Правила:
- Перед любыми изменениями выполнить `git pull`, чтобы убедиться, что рабочая копия актуальна.
- Вносить только небольшие и безопасные правки.
- Сохранять текущий визуальный стиль, если не попросили иначе.
- Не переписывать существующие тексты без явной просьбы.
- Перед редактированием назвать файлы, которые планируется изменить.
- Предпочитать правку существующих файлов созданию новых абстракций.
- Не переименовывать и не перемещать файлы без необходимости.
- Сохранять SEO- и верификационные файлы:
  - CNAME
  - robots.txt
  - sitemap.xml
  - google*.html
  - yandex_*.html
- Не трогать сгенерированные и верификационные файлы без явной просьбы.
- После изменений кратко описать, что именно изменилось.
- Предложить короткое сообщение для git-коммита.
- Если изменение может затронуть несколько страниц — предупредить перед правкой.