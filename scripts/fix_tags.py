import re, os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

tags_html = """<div class="tag-nav">
  <a class="tag-chip" href="tags/knigi.html">#книги</a>
  <a class="tag-chip" href="tags/liderstvo.html">#лидерство</a>
  <a class="tag-chip" href="tags/tsennosti.html">#ценности</a>
</div>"""

with open('_partials/tags-nav.html', 'w') as f:
    f.write(tags_html)
print("_partials/tags-nav.html updated")

files = ['blog/index.html'] + [f'blog/page-{i}.html' for i in range(2, 6)] + [
    'tags/knigi.html',
    'tags/liderstvo.html',
    'tags/tsennosti.html',
]
for fname in files:
    with open(fname) as f: html = f.read()
    html = re.sub(r'<div class="tag-nav">.*?</div>', '<div id="site-tags"></div>', html, flags=re.DOTALL)
    html = html.replace('padding:52px 0 36px', 'padding:52px 0 16px')
    html = html.replace('padding: 52px 0 36px', 'padding: 52px 0 16px')
    with open(fname, 'w') as f: f.write(html)
    print(f"updated: {fname}")
