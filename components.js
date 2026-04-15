(async function() {
  // Determine prefix based on path depth
  const depth = location.pathname.split('/').filter(Boolean).length;
  const prefix = depth >= 2 ? '../' : '';

  async function load(selector, file) {
    const el = document.querySelector(selector);
    if (!el) return;
    try {
      const r = await fetch(prefix + file);
      el.outerHTML = await r.text();
    } catch(e) {}
  }

  await load('#site-header', 'header.html?v=2');
  await load('#site-footer', 'footer.html');

  // Fix all relative links in header to use correct prefix
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
