(async function() {
  const depth = location.pathname.split('/').filter(Boolean).length;
  const prefix = depth >= 2 ? '../' : '';

  async function loadInto(selector, file) {
    const el = document.querySelector(selector);
    if (!el) return;
    try {
      const r = await fetch(prefix + file);
      const html = await r.text();

      // Insert HTML
      el.innerHTML = html;

      // Execute any <script> tags manually (innerHTML doesn't run them)
      el.querySelectorAll('script').forEach(old => {
        const s = document.createElement('script');
        if (old.src) {
          s.src = old.src;
          s.async = old.async;
        } else {
          s.textContent = old.textContent;
        }
        old.parentNode.replaceChild(s, old);
      });
    } catch(e) {}
  }

  await loadInto('#site-header', 'header.html?v=2');
  await loadInto('#site-footer', 'footer.html');

  // Fix header links for subdirectory pages
  document.querySelectorAll('nav a').forEach(a => {
    const href = a.getAttribute('href') || '';
    if (href && !href.startsWith('http') && !href.startsWith('#') && prefix) {
      a.setAttribute('href', prefix + href);
    }
  });

  // Highlight active nav link
  const page = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('nav a.nav-link').forEach(a => {
    const href = (a.getAttribute('href') || '').replace('../', '');
    if (href === page || (page === '' && href === 'index.html')) {
      a.style.color = 'var(--accent)';
      a.style.borderBottomColor = 'var(--accent)';
      a.style.borderBottomWidth = '1px';
      a.style.borderBottomStyle = 'solid';
    }
  });
})();
