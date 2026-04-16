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

  function ensureSharedStylesheet() {
    const id = 'site-components-css';
    if (document.getElementById(id)) return;
    const existing = Array.from(document.querySelectorAll('link[rel=\"stylesheet\"]'))
      .some(l => (l.getAttribute('href') || '').includes('site-components.css'));
    if (existing) return;
    const link = document.createElement('link');
    link.id = id;
    link.rel = 'stylesheet';
    link.href = `${prefix}styles/site-components.css?v=1`;
    document.head.appendChild(link);
  }

  async function loadPostsData() {
    try {
      const r = await fetch(prefix + 'posts.js');
      if (!r.ok) return null;
      const js = await r.text();
      // posts.js is first-party static content in this repo.
      const posts = new Function(js + '; return typeof POSTS !== "undefined" ? POSTS : null;')();
      return Array.isArray(posts) ? posts : null;
    } catch (e) {
      return null;
    }
  }

  async function loadTagSlugMap() {
    const tags = ['knigi', 'liderstvo', 'tsennosti'];
    const map = new Map();
    const toSlugs = html => {
      const out = new Set();
      const re = /posts\/([^/"?#]+)\.html/g;
      let m;
      while ((m = re.exec(html))) out.add(m[1]);
      return out;
    };
    await Promise.all(tags.map(async tag => {
      try {
        const r = await fetch(`${prefix}tag-${tag}.html`);
        if (!r.ok) return;
        const html = await r.text();
        toSlugs(html).forEach(slug => {
          const arr = map.get(slug) || [];
          if (!arr.includes(tag)) arr.push(tag);
          map.set(slug, arr);
        });
      } catch (e) {}
    }));
    return map;
  }

  function pickPrimaryTag(tags) {
    const order = ['knigi', 'liderstvo', 'tsennosti'];
    for (const t of order) {
      if ((tags || []).includes(t)) return t;
    }
    return (tags && tags[0]) || null;
  }

  function tagLabel(tag) {
    if (tag === 'knigi') return '#книги';
    if (tag === 'liderstvo') return '#лидерство';
    if (tag === 'tsennosti') return '#ценности';
    return '';
  }

  const bookCoverCache = new Map();

  async function fetchBookCoverForSlug(slug) {
    if (bookCoverCache.has(slug)) return bookCoverCache.get(slug);
    let result = null;
    try {
      const r = await fetch(`${prefix}posts/${slug}.html`);
      if (!r.ok) {
        bookCoverCache.set(slug, null);
        return null;
      }
      const html = await r.text();
      const coverMatch = /class=\"post-cover\"[\s\S]*?<img[^>]+src=\"([^\"]+)\"[^>]*alt=\"([^\"]*)\"/i.exec(html);
      if (coverMatch) {
        result = { src: coverMatch[1], alt: coverMatch[2] || 'Обложка книги' };
      } else {
        const og = /<meta\s+property=\"og:image\"\s+content=\"([^\"]+)\"/i.exec(html);
        if (og) result = { src: og[1], alt: 'Обложка книги' };
      }
    } catch (e) {
      result = null;
    }
    bookCoverCache.set(slug, result);
    return result;
  }

  function injectBookCoverIntoCard(card, cover) {
    if (!cover || !cover.src) return;
    if (card.querySelector('.card-book-cover')) return;
    const titleEl = card.querySelector('.post-card-title, .blog-card-title');
    if (!titleEl) return;
    const wrap = document.createElement('div');
    wrap.className = 'card-book-cover-wrap';
    const img = document.createElement('img');
    img.className = 'card-book-cover';
    img.src = cover.src;
    img.alt = cover.alt || 'Обложка книги';
    img.loading = 'lazy';
    img.decoding = 'async';
    wrap.appendChild(img);
    titleEl.insertAdjacentElement('afterend', wrap);
  }

  async function hydrateBookCardsWithCover() {
    const cards = Array.from(
      document.querySelectorAll(
        '.post-list .post-card.post-tag-knigi, .post-nav.post-nav-related .blog-card.post-tag-knigi, #homeBlogGrid .blog-card.post-tag-knigi'
      )
    );
    if (!cards.length) return;
    await Promise.all(cards.map(async card => {
      const href = card.getAttribute('href') || '';
      const m = /posts\/([^/]+)\.html$/.exec(href);
      if (!m) return;
      const cover = await fetchBookCoverForSlug(m[1]);
      injectBookCoverIntoCard(card, cover);
    }));
  }

  function formatDateRu(dateRaw) {
    const m = /^(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})$/.exec(String(dateRaw || '').trim());
    if (!m) return String(dateRaw || '').toUpperCase();
    const months = {
      january: 'ЯНВАРЯ',
      february: 'ФЕВРАЛЯ',
      march: 'МАРТА',
      april: 'АПРЕЛЯ',
      may: 'МАЯ',
      june: 'ИЮНЯ',
      july: 'ИЮЛЯ',
      august: 'АВГУСТА',
      september: 'СЕНТЯБРЯ',
      october: 'ОКТЯБРЯ',
      november: 'НОЯБРЯ',
      december: 'ДЕКАБРЯ'
    };
    const day = m[1];
    const month = months[m[2].toLowerCase()] || m[2].toUpperCase();
    return `${day} ${month} ${m[3]}`;
  }

  function escapeHtml(s) {
    return String(s || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function truncText(s, max) {
    const v = String(s || '').trim();
    return v.length > max ? `${v.slice(0, max).trimEnd()}…` : v;
  }

  function getNearbyPostIndexes(posts, currentIndex, count) {
    const out = [];
    for (let step = 1; out.length < count && step < posts.length; step++) {
      const left = currentIndex - step;
      const right = currentIndex + step;
      if (left >= 0) out.push(left);
      if (out.length >= count) break;
      if (right < posts.length) out.push(right);
    }
    return out.slice(0, count);
  }

  function renderRelatedPosts(posts, tagSlugMap) {
    const m = /\/posts\/([^/]+)\.html$/.exec(location.pathname);
    if (!m) return;
    const slug = m[1];
    const currentIndex = posts.findIndex(p => p.slug === slug);
    if (currentIndex === -1) return;

    const nav = document.querySelector('.post-nav');
    if (!nav) return;

    const idxs = getNearbyPostIndexes(posts, currentIndex, 3);
    const nearby = idxs.map(i => posts[i]).filter(Boolean);
    if (!nearby.length) return;

    nav.classList.add('post-nav-related');
    nav.innerHTML = `<div class="post-related-grid">${
      nearby.map(p => {
        const tags = tagSlugMap.get(p.slug) || [];
        const tagClass = tags.map(t => `post-tag-${t}`).join(' ');
        const primaryTag = pickPrimaryTag(tags);
        const hash = primaryTag ? `<div class="blog-card-hash">${escapeHtml(tagLabel(primaryTag))}</div>` : '';
        return `
        <a href="${p.slug}.html" class="blog-card post-related-card ${tagClass}">
          <div class="blog-card-date">${escapeHtml(formatDateRu(p.date))}</div>
          <div class="blog-card-title">${escapeHtml(truncText(p.title, 95))}</div>
          <div class="blog-card-desc">${escapeHtml(truncText(p.description, 180))}</div>
          ${hash}
        </a>
      `;
      }).join('')
    }</div>`;
  }

  function hydratePostListCards(posts, tagSlugMap) {
    const cards = document.querySelectorAll(
      '.post-list .post-card[href*="/posts/"], .post-list .post-card[href^="posts/"], #homeBlogGrid .blog-card[href*="posts/"], #homeBlogGrid .blog-card[href^="posts/"]'
    );
    if (!cards.length) return;
    const bySlug = new Map(posts.map(p => [p.slug, p]));
    cards.forEach(card => {
      const href = card.getAttribute('href') || '';
      const m = /posts\/([^/]+)\.html$/.exec(href);
      if (!m) return;
      const post = bySlug.get(m[1]);
      if (!post) return;
      const t = card.querySelector('.post-card-title, .blog-card-title');
      const d = card.querySelector('.post-card-desc, .blog-card-desc');
      if (t) t.textContent = truncText(post.title, 95);
      if (d) d.textContent = truncText(post.description, 180);
      const tags = tagSlugMap.get(post.slug) || [];
      tags.forEach(tag => card.classList.add(`post-tag-${tag}`));
      const primaryTag = pickPrimaryTag(tags);
      if (!card.classList.contains('post-card')) return;
      let hash = card.querySelector('.post-card-hash');
      if (!hash && primaryTag) {
        hash = document.createElement('div');
        hash.className = 'post-card-hash';
        card.appendChild(hash);
      }
      if (hash) hash.textContent = tagLabel(primaryTag);
    });
  }

  function addPostHeaderBlogLink() {
    if (!/\/posts\/[^/]+\.html$/.test(location.pathname)) return;
    const dateEl = document.querySelector('.post-date');
    if (!dateEl) return;
    if (dateEl.querySelector('.post-date-link')) return;
    const link = document.createElement('a');
    link.className = 'post-date-link';
    link.href = `${prefix}blog.html`;
    link.textContent = 'Все посты';
    dateEl.appendChild(link);
  }

  ensureSharedStylesheet();
  await load('#site-header', 'header.html?v=5');
  await load('#site-footer', 'footer.html');
  await loadTagNav();
  const postsData = await loadPostsData();
  const tagSlugMap = await loadTagSlugMap();
  if (postsData) {
    renderRelatedPosts(postsData, tagSlugMap);
    hydratePostListCards(postsData, tagSlugMap);
    hydrateBookCardsWithCover();
  }
  addPostHeaderBlogLink();

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
  if (page === 'tag-knigi.html') document.body.classList.add('tag-theme-knigi');
  if (page === 'tag-liderstvo.html') document.body.classList.add('tag-theme-liderstvo');
  if (page === 'tag-tsennosti.html') document.body.classList.add('tag-theme-tsennosti');
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
