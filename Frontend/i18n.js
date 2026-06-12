(function () {
  const savedLanguage = localStorage.getItem('preferred_language') || 'en';

  // Function to translate static DOM elements containing data-i18n attributes
  window.updateI18nContent = function () {
    if (typeof i18next === 'undefined') {
      console.warn('i18next is not loaded yet.');
      return;
    }

    document.querySelectorAll('[data-i18n]').forEach((element) => {
      const key = element.getAttribute('data-i18n');
      element.innerHTML = i18next.t(key);
    });

    document.querySelectorAll('[data-i18n-placeholder]').forEach((element) => {
      const key = element.getAttribute('data-i18n-placeholder');
      element.setAttribute('placeholder', i18next.t(key));
    });

    // Update document title if applicable
    const isAnalysisPage = window.location.pathname.includes('analysis.html');
    const titleKey = isAnalysisPage ? 'document_title_analysis' : 'document_title_home';
    document.title = i18next.t(titleKey);

    // Update html lang attribute
    document.documentElement.setAttribute('lang', i18next.language);
  };

  // Run initialization after i18next and translations.js are loaded
  function initI18n() {
    if (typeof i18next === 'undefined' || typeof window.translations === 'undefined') {
      setTimeout(initI18n, 50);
      return;
    }

    i18next.init(
      {
        lng: savedLanguage,
        fallbackLng: 'en',
        resources: window.translations,
      },
      function (err, t) {
        if (err) return console.error('i18next init error:', err);

        // Update static layout content
        window.updateI18nContent();

        // Bind dropdown states
        document.addEventListener('DOMContentLoaded', () => {
          setupDropdown();
        });

        // Also check if DOM is already loaded
        if (document.readyState === 'interactive' || document.readyState === 'complete') {
          setupDropdown();
        }
      }
    );
  }

  function setupDropdown() {
    const select = document.getElementById('language-select');
    if (!select) return;

    select.value = i18next.language;

    // Single listener execution guard
    if (select.dataset.listenerBound === 'true') return;
    select.dataset.listenerBound = 'true';

    select.addEventListener('change', (e) => {
      const lang = e.target.value;
      i18next.changeLanguage(lang, (err) => {
        if (err) return console.error('changeLanguage error:', err);

        localStorage.setItem('preferred_language', lang);
        window.updateI18nContent();

        // Fire global custom event to notify external page scripts (like analysis.js)
        window.dispatchEvent(
          new CustomEvent('languagechange', {
            detail: { language: lang },
          })
        );
      });
    });
  }

  initI18n();
})();
