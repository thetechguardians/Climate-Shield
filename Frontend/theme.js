(function () {
  const saved = localStorage.getItem('theme');
  const preferred = window.matchMedia('(prefers-color-scheme: light)').matches
    ? 'light' : 'dark';
  const initial = saved || preferred;

  document.documentElement.setAttribute('data-theme', initial);

  document.addEventListener('DOMContentLoaded', function () {
    const btn  = document.getElementById('theme-toggle');
    const icon = document.getElementById('theme-icon');

    if (!btn || !icon) return;

    icon.textContent = initial === 'light' ? '🌙' : '☀️';

    btn.addEventListener('click', function () {
      const current = document.documentElement.getAttribute('data-theme');
      const next    = current === 'dark' ? 'light' : 'dark';

      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
      icon.textContent = next === 'light' ? '🌙' : '☀️';

      // Notify analysis.js to swap the map tile layer if it's listening
      window.dispatchEvent(new CustomEvent('themechange', { detail: { theme: next } }));
    });
  });
})();
