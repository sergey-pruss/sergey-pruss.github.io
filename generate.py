#!/usr/bin/env python3
"""
Генератор постов и страниц блога.
Запускать после изменений в posts.js или добавления новых постов.
"""
import re, os, json

def analytics_head(script_prefix: str) -> str:
    """script_prefix: '' с корня сайта, '../' из /blog/ и /posts/. См. scripts/analytics.js."""
    return f'''<!-- Счётчики: scripts/analytics.js -->
<script src="{script_prefix}scripts/analytics.js" defer></script>
<noscript><div><img src="https://mc.yandex.ru/watch/108559120" style="position:absolute; left:-9999px;" alt="" /><img src="https://top-fwz1.mail.ru/counter?id=3759565;js=na" style="position:absolute; left:-9999px;" alt="Top.Mail.Ru" /></div></noscript>'''

PER_PAGE = 42

MONTHS_RU = {'January':'января','February':'февраля','March':'марта','April':'апреля',
             'May':'мая','June':'июня','July':'июля','August':'августа',
             'September':'сентября','October':'октября','November':'ноября','December':'декабря'}

def ru_date(d):
    for en, ru in MONTHS_RU.items(): d = d.replace(en, ru)
    return d

def esc(s):
    return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

TRUNC_STOPWORDS = {
    'и', 'а', 'но', 'или', 'либо', 'да', 'что', 'чтобы', 'как',
    'в', 'во', 'на', 'с', 'со', 'к', 'ко', 'у', 'о', 'об', 'обо',
    'по', 'за', 'для', 'про', 'под', 'над', 'из', 'изо', 'до', 'при', 'от', 'без',
    'не', 'ни', 'же', 'ли', 'бы'
}

def _trim_trunc_end(s):
    return re.sub(r'[\s,;:!?.…–—-]+$', '', s).strip()

def _fix_dangling_stopword_fragment(s):
    v = re.sub(r'\s+', ' ', s or '').strip()
    if not v:
        return v
    if re.search(r'[.!?…]$', v):
        return v

    words = v.split()
    changed = False
    while len(words) > 1 and words[-1].lower() in TRUNC_STOPWORDS:
        words.pop()
        changed = True
    if not changed:
        return v
    return _trim_trunc_end(' '.join(words)) + '...'

def trunc(s, n):
    v = re.sub(r'\s+', ' ', s or '').strip()
    if len(v) <= n:
        return _fix_dangling_stopword_fragment(v)

    probe = v[:n + 1]
    boundary = probe.rfind(' ')
    if boundary < int(n * 0.55):
        boundary = n

    candidate = _trim_trunc_end(v[:boundary])
    if not candidate:
        candidate = _trim_trunc_end(v[:n])

    words = candidate.split()
    while len(words) > 1 and words[-1].lower() in TRUNC_STOPWORDS:
        words.pop()
    candidate = ' '.join(words).strip()
    if not candidate:
        candidate = _trim_trunc_end(v[:n])

    return candidate + '...'

def get_style():
    with open('index.html') as f: html = f.read()
    return re.search(r'<style>(.*?)</style>', html, re.DOTALL).group(1)

def get_entries():
    with open('posts.js') as f: js = f.read()
    return re.findall(r'\{slug:`([^`]+)`,date:`([^`]+)`,title:`((?:[^`]|\\`)*?)`,description:`((?:[^`]|\\`)*?)`\}', js)

# ─── POST TEMPLATE (сейчас не собирается этим скриптом) ───────────
# При сборке постов подставлять metrika=analytics_head('../').
POST_HEAD = '''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title_esc} — Сергей Прусс</title>
<meta name="description" content="{desc_esc}">
<meta name="author" content="Сергей Прусс">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://sergeypruss.ru/posts/{slug}.html">
<meta property="og:type" content="article">
<meta property="og:url" content="https://sergeypruss.ru/posts/{slug}.html">
<meta property="og:title" content="{title_esc} — Сергей Прусс">
<meta property="og:description" content="{desc_esc}">
<meta property="og:image" content="{og_image}">
<meta property="og:locale" content="ru_RU">
<meta property="article:published_time" content="{pub_date}">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Article","headline":"{title_esc}","description":"{desc_esc}","datePublished":"{pub_date}","url":"https://sergeypruss.ru/posts/{slug}.html","image":"{og_image}","author":{{"@type":"Person","name":"Сергей Прусс","url":"https://sergeypruss.ru"}}}}
</script>
{metrika}
<style>{style}
  .post-header{{padding:52px 0 28px}}.post-date{{font-size:.7rem;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-soft);margin-bottom:16px}}.post-title{{font-family:'Museo Sans',sans-serif;font-size:clamp(1.6rem,5vw,2.4rem);font-weight:700;line-height:1.2}}
  .post-body{{padding-bottom:0}}.post-body p{{font-size:1rem;line-height:1.82;margin-bottom:1.4em;color:var(--ink)}}.post-body p:last-child{{margin-bottom:0}}
  .post-photos img{{width:100%;border-radius:8px;display:block}}
  .post-cta{{margin-top:52px;padding-top:32px;border-top:1px solid var(--line);font-size:.97rem;color:var(--ink-soft);line-height:1.7}}.post-cta a{{color:var(--accent);text-decoration:none;border-bottom:1px solid var(--accent);transition:opacity .2s}}.post-cta a:hover{{opacity:.7}}
  .post-nav{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:40px;padding:40px 0 80px;border-top:1px solid var(--line)}}.post-nav-item{{text-decoration:none;display:block}}.post-nav-label{{font-size:.65rem;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-soft);margin-bottom:8px}}.post-nav-title{{font-size:.92rem;line-height:1.4;color:var(--ink);font-weight:500;transition:color .2s}}.post-nav-item:hover .post-nav-title{{color:var(--accent)}}.post-nav-item.next{{text-align:right}}
  @media(max-width:600px){{.post-nav{{grid-template-columns:1fr}}.post-nav-item.next{{text-align:left}}}}
</style></head>'''

# ─── BLOG PAGE TEMPLATE ──────────────────────────────────────────
BLOG_HEAD = '''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title_tag}</title>
<meta name="description" content="Заметки о культуре, управлении и бизнесе от Сергея Прусса">
{metrika}
<link rel="stylesheet" href="{styles_prefix}styles/site.css?v=2">
<link rel="stylesheet" href="{styles_prefix}styles/site-components.css?v=2">
</head>'''


def build_blog_pages():
    entries = get_entries()
    total = len(entries)
    total_pages = (total + PER_PAGE - 1) // PER_PAGE

    def pag_root(cur):
        parts = ['<div class="pagination">']
        if cur > 1: parts.append(f'<a href="{"blog.html" if cur==2 else f"blog/page-{cur-1}.html"}" class="page-btn">← Назад</a>')
        for i in range(1, total_pages+1):
            parts.append(f'<a href="{"blog.html" if i==1 else f"blog/page-{i}.html"}" class="page-btn{"  active" if i==cur else ""}">{i}</a>')
        if cur < total_pages: parts.append(f'<a href="blog/page-{cur+1}.html" class="page-btn">Вперёд →</a>')
        parts.append('</div>'); return '\n'.join(parts)

    def pag_sub(cur):
        parts = ['<div class="pagination">']
        if cur > 1: parts.append(f'<a href="{"../blog.html" if cur==2 else f"../blog/page-{cur-1}.html"}" class="page-btn">← Назад</a>')
        for i in range(1, total_pages+1):
            parts.append(f'<a href="{"../blog.html" if i==1 else f"../blog/page-{i}.html"}" class="page-btn{"  active" if i==cur else ""}">{i}</a>')
        if cur < total_pages: parts.append(f'<a href="../blog/page-{cur+1}.html" class="page-btn">Вперёд →</a>')
        parts.append('</div>'); return '\n'.join(parts)

    def cards(page_e, prefix=''):
        return '\n'.join(f'''    <a class="post-card" href="{prefix}posts/{s}.html">
      <div class="post-card-date">{esc(ru_date(d))}</div>
      <div class="post-card-title">{esc(trunc(t.replace(chr(92)+'`','`'),60))}</div>
      {f'<div class="post-card-desc">{esc(trunc(desc.replace(chr(92)+"` ","`"),90))}</div>' if desc else ''}
    </a>''' for s,d,t,desc in page_e)

    def page(title_tag, cards_html, pagination, prefix):
        head = BLOG_HEAD.format(title_tag=title_tag, metrika=analytics_head(prefix), styles_prefix=prefix)
        return f'''{head}
<body>
<div id="site-header"></div>
<div class="wrap">
  <div class="blog-header"><h1>Блог</h1><p class="sub">Заметки о культуре, управлении и бизнесе</p></div>
  <div id="site-tags"></div>
  <div class="post-list">
{cards_html}
  </div>
{pagination}
</div>
<div id="site-footer"></div>
<script src="{prefix}components.js"></script>
</body></html>'''

    with open('blog.html','w') as f:
        f.write(page('Блог — Сергей Прусс', cards(entries[:PER_PAGE]), pag_root(1), ''))

    os.makedirs('blog', exist_ok=True)
    for p in range(2, total_pages+1):
        with open(f'blog/page-{p}.html','w') as f:
            f.write(page(f'Блог, страница {p} — Сергей Прусс', cards(entries[(p-1)*PER_PAGE:p*PER_PAGE], '../'), pag_sub(p), '../'))

    print(f"Blog: {total} posts, {total_pages} pages")


if __name__ == '__main__':
    build_blog_pages()
    print("Done. Run: python3 typograph.py")


def build_sitemap():
    """Генерирует sitemap.xml из текущего posts.js"""
    from datetime import datetime

    entries = get_entries()
    BASE = 'https://sergeypruss.ru'
    today = datetime.now().strftime('%Y-%m-%d')

    MONTHS_EN = {'January':'01','February':'02','March':'03','April':'04','May':'05','June':'06',
                 'July':'07','August':'08','September':'09','October':'10','November':'11','December':'12'}

    def iso_date(d):
        import re
        m = re.match(r'(\d+) (\w+) (\d+)', d)
        if m:
            return f"{m.group(3)}-{MONTHS_EN.get(m.group(2),'01')}-{m.group(1).zfill(2)}"
        return today

    total = len(entries)
    total_pages = (total + PER_PAGE - 1) // PER_PAGE

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']

    for url, lastmod, priority in [('', today, '1.0'), ('blog.html', today, '0.9')]:
        lines.append(f'  <url>\n    <loc>{BASE}/{url}</loc>\n    <lastmod>{lastmod}</lastmod>\n    <priority>{priority}</priority>\n  </url>')

    for i in range(2, total_pages + 1):
        lines.append(f'  <url>\n    <loc>{BASE}/blog/page-{i}.html</loc>\n    <lastmod>{today}</lastmod>\n    <priority>0.7</priority>\n  </url>')

    for slug, date, *_ in entries:
        lines.append(f'  <url>\n    <loc>{BASE}/posts/{slug}.html</loc>\n    <lastmod>{iso_date(date)}</lastmod>\n    <priority>0.8</priority>\n  </url>')

    lines.append('</urlset>')
    with open('sitemap.xml', 'w') as f:
        f.write('\n'.join(lines))

    print(f"sitemap.xml: {total + 1 + total_pages} URLs")


if __name__ == '__main__':
    build_blog_pages()
    build_sitemap()
    print("Done. Run: python3 typograph.py")
