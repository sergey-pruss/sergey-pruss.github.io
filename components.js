(async function() {
  const depth = location.pathname.split('/').filter(Boolean).length;
  const prefix = depth >= 2 ? '../' : '';

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

  await load('#site-header', 'header.html?v=2');
  await load('#site-footer', 'footer.html');

  // Fix header links for subdirectory pages
  document.querySelectorAll('nav a').forEach(a => {
    const href = a.getAttribute('href') || '';
    if (href && !href.startsWith('http') && !href.startsWith('#') && prefix) {
      a.setAttribute('href', prefix + href);
    }
  });

  // Highlight active nav link
  const page = location.pathname.split('/').pop() || 'index.html';
  const isTagPage = /^tag-(knigi|liderstvo|tsennosti)\.html$/.test(page);
  document.querySelectorAll('nav a.nav-link').forEach(a => {
    const href = (a.getAttribute('href') || '').replace('../', '');
    if (href === page || (page === '' && href === 'index.html') || (isTagPage && href === 'blog.html')) {
      a.style.color = 'var(--accent)';
      a.style.borderBottomColor = 'var(--accent)';
      a.style.borderBottomWidth = '1px';
      a.style.borderBottomStyle = 'solid';
    }
  });
})();
