(async function() {
  const depth = location.pathname.split('/').filter(Boolean).length;
  const prefix = depth >= 2 ? '../' : '';

  /** Синхронно с tags.html — подставляется, если fetch недоступен или файл не задеплоен */
  const TAG_NAV_HTML = `<div class="tag-nav">
  <a class="tag-chip" href="tag-knigi.html">#книги</a>
  <a class="tag-chip" href="tag-liderstvo.html">#лидерство</a>
  <a class="tag-chip" href="tag-tsennosti.html">#ценности</a>
</div>`;

  function injectHTML(container, html) {
    // Parse and insert — scripts must be recreated to execute
    const tmp = document.createElement('div');
    tmp.innerHTML = html;

    // Move all nodes except scripts first
    Array.from(tmp.childNodes).forEach(node => {
      if (node.nodeName !== 'SCRIPT') {
        container.parentNode.insertBefore(node.cloneNode(true), container.nextSibling);
      }
    });

    // Then create and append script elements so they execute
    tmp.querySelectorAll('script').forEach(oldScript => {
      const s = document.createElement('script');
      Array.from(oldScript.attributes).forEach(a => s.setAttribute(a.name, a.value));
      s.textContent = oldScript.textContent;
      document.body.appendChild(s);
    });

    container.remove();
  }

  async function load(selector, file) {
    const el = document.querySelector(selector);
    if (!el) return;
    try {
      const r = await fetch(prefix + file);
      const html = await r.text();
      injectHTML(el, html);
    } catch(e) {}
  }

  async function loadTagNav() {
    const el = document.querySelector('#site-tags');
    if (!el) return;
    let html = TAG_NAV_HTML;
    try {
      const r = await fetch(prefix + 'tags.html');
      if (r.ok) {
        const t = (await r.text()).trim();
        if (t) html = t;
      }
    } catch (e) {}
    injectHTML(el, html);
  }

  await load('#site-header', 'header.html?v=4');
  await load('#site-footer', 'footer.html');
  await loadTagNav();

  // Fix header links for subdirectory pages
  document.querySelectorAll('nav a').forEach(a => {
    const href = a.getAttribute('href') || '';
    if (href && !href.startsWith('http') && !href.startsWith('#') && prefix) {
      a.setAttribute('href', prefix + href);
    }
  });

  document.querySelectorAll('.tag-nav a.tag-chip').forEach(a => {
    const href = a.getAttribute('href') || '';
    if (href && !href.startsWith('http') && !href.startsWith('#') && prefix) {
      a.setAttribute('href', prefix + href);
    }
  });

  const pageFile = location.pathname.split('/').pop() || 'index.html';
  if (/^tag-[^/]+\.html$/.test(pageFile)) {
    document.querySelectorAll('.tag-nav .tag-chip').forEach(a => {
      const chipHref = (a.getAttribute('href') || '').replace(/^\.\.\//, '');
      const chipFile = chipHref.split('/').pop();
      if (chipFile === pageFile) a.classList.add('active');
    });
  }

  // Highlight active nav link
  const page = location.pathname.split('/').pop() || 'index.html';
  const isTagPage = /^tag-(knigi|liderstvo|tsennosti)\.html$/.test(page);
  const isPostPage = /\/posts\/[^/]+\.html$/.test(location.pathname);
  const isBlogPaginationPage = /\/blog\/page-\d+\.html$/.test(location.pathname);
  document.querySelectorAll('nav a.nav-link').forEach(a => {
    const href = (a.getAttribute('href') || '').replace('../', '');
    if (
      href === page ||
      (page === '' && href === 'index.html') ||
      ((isTagPage || isPostPage || isBlogPaginationPage) && href === 'blog.html')
    ) {
      a.style.color = 'var(--accent)';
      a.style.borderBottomColor = 'var(--accent)';
      a.style.borderBottomWidth = '1px';
      a.style.borderBottomStyle = 'solid';
    }
  });
})();
