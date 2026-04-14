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
  await load('#site-header', 'header.html');
  await load('#site-footer', 'footer.html');
})();
