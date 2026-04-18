This is Sergey Pruss's personal static website.

Project structure:
- Main pages: index.html, blog.html
- Shared fragments: header.html, footer.html
- Content/data files: posts.js, components.js
- Assets: img/, fonts/, files/
- Utility scripts: generate.py, typograph.py

Rules:
- Make only small, safe edits.
- Preserve the current visual style unless explicitly asked.
- Do not rewrite existing texts unless requested.
- Before editing, name the files you plan to change.
- Prefer editing existing files over creating new abstractions.
- Do not rename or move files unless necessary.
- Preserve SEO files and verification files:
  - CNAME
  - robots.txt
  - sitemap.xml
  - google*.html
  - yandex_*.html
- Do not touch generated or verification files unless explicitly asked.
- After changes, summarize exactly what changed.
- Suggest a short git commit message.
- If a change may affect multiple pages, warn before editing.