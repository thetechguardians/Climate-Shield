(function () {
  function getSystemPreference() {
    return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
  }

  const saved = localStorage.getItem('theme');
  let initial = saved || getSystemPreference();

  document.documentElement.setAttribute('data-theme', initial);

  // Listen for system theme changes dynamically
  window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', function(e) {
    // Only apply system theme if the user hasn't set a manual override
    if (!localStorage.getItem('theme')) {
      const newTheme = e.matches ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', newTheme);
      
      const icon = document.getElementById('theme-icon');
      if (icon) {
        icon.textContent = newTheme === 'light' ? '🌙' : '☀️';
      }
      
      window.dispatchEvent(new CustomEvent('themechange', { detail: { theme: newTheme } }));
    }
  });

  document.addEventListener('DOMContentLoaded', function () {
    const btn  = document.getElementById('theme-toggle');
    const icon = document.getElementById('theme-icon');

    if (!btn || !icon) return;

    // Set initial icon state based on the calculated initial theme
    icon.textContent = document.documentElement.getAttribute('data-theme') === 'light' ? '🌙' : '☀️';

    btn.addEventListener('click', function () {
      const current = document.documentElement.getAttribute('data-theme');
      const next    = current === 'dark' ? 'light' : 'dark';

      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('theme', next); // User manually set a theme
      icon.textContent = next === 'light' ? '🌙' : '☀️';

      // Notify analysis.js to swap the map tile layer if it's listening
      window.dispatchEvent(new CustomEvent('themechange', { detail: { theme: next } }));
    });
  });
})();
