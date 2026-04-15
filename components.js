(async function() {
  async function load(selector, file) {
    const el = document.querySelector(selector);
    if (!el) return;
    try {
      const r = await fetch(file);
      const html = await r.text();
      el.outerHTML = html;
    } catch(e) {
      console.warn('Could not load', file, e);
    }
  }
  await load('#site-header', 'header.html?v=2');
  await load('#site-footer', 'footer.html');

  // Highlight active nav link
  const page = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('nav a.nav-link').forEach(a => {
    const href = a.getAttribute('href') || '';
    if (href && (href === page || (page === '' && href === 'index.html'))) {
      a.style.color = 'var(--accent)';
      a.style.borderBottomColor = 'var(--accent)';
      a.style.borderBottomWidth = '1px';
      a.style.borderBottomStyle = 'solid';
      a.style.paddingBottom = '2px';
    }
  });
})();
