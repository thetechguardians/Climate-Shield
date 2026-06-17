i18next
  .use(i18nextHttpBackend)
  .use(i18nextBrowserLanguageDetector)
  .init({
    fallbackLng: 'en',
    backend: {
      loadPath: '/locales/{{lng}}/translation.json',
    }
  }).then(() => {
    const initLangSync = () => {
      updateContent();
      const langSelect = document.getElementById('langSelect');
      if (langSelect && i18next.language) {
        const baseLang = i18next.language.split('-')[0];
        langSelect.value = baseLang;
      }
    };

    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', initLangSync);
    } else {
      initLangSync();
    }
  });

function updateContent() {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (el.tagName === 'INPUT' && el.placeholder) {
      el.placeholder = i18next.t(key);
    } else {
      el.innerHTML = i18next.t(key);
    }
  });
}

window.changeLanguage = function(lng) {
  i18next.changeLanguage(lng).then(() => {
    updateContent();
    const langSelect = document.getElementById('langSelect');
    if (langSelect && i18next.language) {
      const baseLang = i18next.language.split('-')[0];
      langSelect.value = baseLang;
    }
  });
}

// Intercept chatbot submissions to pass current language
document.addEventListener('DOMContentLoaded', () => {
    // Override the native fetch to append language if hitting our endpoints
    const originalFetch = window.fetch;
    window.fetch = function() {
        let [resource, config] = arguments;
        if (typeof resource === 'string' && (resource.includes('/chatbot') || resource.includes('/weather'))) {
            if (config && config.body && typeof config.body === 'string') {
                try {
                    let bodyObj = JSON.parse(config.body);
                    bodyObj.lang = i18next.language || 'en';
                    config.body = JSON.stringify(bodyObj);
                } catch(e) {}
            }
        }
        return originalFetch.apply(this, arguments);
    };
});
