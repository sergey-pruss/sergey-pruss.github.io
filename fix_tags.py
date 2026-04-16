import re

tags_html = """<div class="tag-nav">
  <a class="tag-chip" href="tag-knigi.html">#книги</a>
  <a class="tag-chip" href="tag-liderstvo.html">#лидерство</a>
  <a class="tag-chip" href="tag-tsennosti.html">#ценности</a>
</div>"""

with open('tags.html', 'w') as f:
    f.write(tags_html)
print("tags.html created")

files = ['blog.html'] + [f'blog/page-{i}.html' for i in range(2, 6)] + [
    'tag-knigi.html',
    'tag-liderstvo.html',
    'tag-tsennosti.html',
]
for fname in files:
    with open(fname) as f: html = f.read()
    html = re.sub(r'<div class="tag-nav">.*?</div>', '<div id="site-tags"></div>', html, flags=re.DOTALL)
    html = html.replace('padding:52px 0 36px', 'padding:52px 0 16px')
    html = html.replace('padding: 52px 0 36px', 'padding: 52px 0 16px')
    with open(fname, 'w') as f: f.write(html)
    print(f"updated: {fname}")
