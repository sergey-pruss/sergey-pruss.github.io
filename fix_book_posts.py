#!/usr/bin/env python3
"""
Для постов с #книги: добавить обложку (og:image) + аккуратно разделить склеенные заголовки карточек.
Без эвристики «переноса хвоста при строчной букве» — она ломала разметку.
"""
import glob
import os
import re
import subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
POSTS = os.path.join(BASE, "posts")

# Минимальная длина левой части заголовка после разреза
MIN_LEFT = 12

# Длинные маркеры первыми. Только явные начала второй фразы, ошибочно попавшей в title.
# Ведущий пробел снижает ложные срабатывания; хвостовой пробел не обязателен (часть# заголовков заканчивается ровно на границе маркера).
MARKERS = [
    " Сильные команды - не те, где нет напряжения, а те, где с ним",
    " Обратная связь должна быть конкретной и про действия",
    " Одна из ключевых черт сильной компании - способность честно смотреть на",
    " Никакие действия не будут точными, если",
    " Процессы нужны",
    " ВкусВилл смотрит на людей как на самостоятельных, взрослых партнёров",
    " Во время ковида команда сама собрала систему доставки за пару недель -",
    " Роль лидера в логике Восьмого навыка",
    " Отдельная важная линия книги - отношение к критике Холидей",
    " Большой блок книги посвящен неудачам",
    " Сильная команда начинается с отбора",
    " Чтобы расти, нужно не расширяться, а фокусироваться",
    " Великие компании выбирают одно",
    " Великие компании делают выбор, исходя из",
    " Великие результаты - не следствие одного гениального решения",
    " Одна из самых сильных идей книги - продуктивная паранойя",
    " Один из самых важных выводов книги в том, что",
    " Молчание выглядит безопасным, но именно оно губительно",
    " Основной барьер - страх испортить отношения",
    " Стратегия отстранения ",
    " Стратегия движения ",
    " Идеализированный образ формирует ",
    " По мере усиления ",
    " Практический фокус для руководителя ",
    " Потеря контакта с реальным Я ",
    " Метрики важны, но они не заменяют",
    " Структура определяет, кто кому",
    " Антихрупкость - это образ",
    " Главное - способность адаптироваться",
    " Не трогай, если работает",
    " Одна из базовых идей книги - эго искажает реальность Холидей",
    " Сильные не воспринимают сложность",
    " Сильные не привязываются к одному",
    " Суть не в том, чтобы сделать все и сразу, а в том,",
    " Великие компании не гонятся за новыми",
    " Понятие «голос» у",
    " Отдельный акцент",
    " На уровне организаций",
    " Бирюзовые компании ",
    " Отсутствие начальников ",
    " Большинство компаний ",
    " Первые версии ",
    " Хорошая команда ",
    " Сильные специалисты находят ",
    " Кови ",
    " Коллинз ",
    " Хорни ",
    " Холидей ",
    " В иерархических ",
    " Инновационные проекты ",
]

COVER_CSS = (
    ".post-cover{margin:0 0 1.35em;display:inline-block;max-width:min(380px,100%);"
    "vertical-align:top;box-sizing:border-box}"
    ".post-cover img{display:block;width:auto;max-width:100%;height:auto;"
    "border-radius:8px;border:1px solid var(--line)}"
)


def dims(path):
    try:
        out = subprocess.check_output(
            ["sips", "-g", "pixelWidth", "-g", "pixelHeight", path],
            stderr=subprocess.DEVNULL,
        ).decode()
        w = int(re.search(r"pixelWidth: (\d+)", out).group(1))
        h = int(re.search(r"pixelHeight: (\d+)", out).group(1))
        return w, h
    except Exception:
        return None, None


def split_by_marker(title):
    t = title.strip()
    best_i = None
    for m in MARKERS:
        i = t.find(m)
        if i == -1:
            continue
        if i < MIN_LEFT:
            continue
        if best_i is None or i < best_i:
            best_i = i
    if best_i is not None:
        left = t[:best_i].strip()
        right = t[best_i:].strip()
        if left and right:
            return left, right
    return t, ""


def fix_card(title, body):
    body = body or ""
    while True:
        t1, extra = split_by_marker(title)
        if not extra:
            break
        body = (extra + " " + body).strip()
        title = t1
    return title, body


def og_to_rel(url):
    m = re.search(r"/img/posts/(.+)$", url)
    if not m:
        return None
    return "../img/posts/" + m.group(1)


def add_cover_css(html):
    if ".post-cover{" in html:
        return html
    needle = ".post-body h2{margin-bottom:calc(.83em + 3px)}"
    if needle not in html:
        return html
    return html.replace(needle, needle + COVER_CSS, 1)


def add_cover_figure(html, rel, w, h):
    if 'class="post-cover"' in html:
        return html
    ogt = re.search(r'<meta property="og:title" content="([^"]*)"', html)
    book = "книга"
    if ogt:
        book = ogt.group(1).split(" — ")[0].replace('"', "'")
    wh = ""
    if w and h:
        wh = f' width="{w}" height="{h}"'
    fig = (
        f'<figure class="post-cover"><img src="{rel}" alt="Обложка: {book}"{wh} '
        f'loading="lazy" decoding="async"></figure>'
    )
    return html.replace('<div class="post-body">', '<div class="post-body">' + fig, 1)


def process_cards(html):
    def repl_article(m):
        inner = m.group(1)
        tm = re.search(r"<h3 class=\"post-card-title\">([^<]*)</h3>", inner)
        bm = re.search(r"<p class=\"post-card-text\">([^<]*)</p>", inner)
        if not tm or not bm:
            return m.group(0)
        title, body = fix_card(tm.group(1), bm.group(1))
        inner = inner.replace(tm.group(0), f'<h3 class="post-card-title">{title}</h3>', 1)
        inner = inner.replace(bm.group(0), f'<p class="post-card-text">{body}</p>', 1)
        return '<article class="post-card">' + inner + "</article>"

    return re.sub(
        r"<article class=\"post-card\">(.*?)</article>", repl_article, html, flags=re.DOTALL
    )


def main():
    for path in sorted(glob.glob(os.path.join(POSTS, "*.html"))):
        with open(path, encoding="utf-8") as f:
            html = f.read()
        if "tag-knigi.html" not in html:
            continue
        ogm = re.search(
            r'<meta property="og:image" content="(https://sergeypruss\.ru/img/posts/[^"]+)"',
            html,
        )
        rel = og_to_rel(ogm.group(1)) if ogm else None
        w = h = None
        if rel:
            img_path = os.path.join(BASE, "img/posts", os.path.basename(rel))
            if os.path.isfile(img_path):
                w, h = dims(img_path)
        html2 = add_cover_css(html)
        if rel:
            html2 = add_cover_figure(html2, rel, w, h)
        html2 = process_cards(html2)
        if html2 != html:
            with open(path, "w", encoding="utf-8") as f:
                f.write(html2)
            print("updated:", os.path.basename(path))


if __name__ == "__main__":
    main()
