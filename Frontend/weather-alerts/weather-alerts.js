/*
 * Subscribe to Climate Alerts — issue #72.
 *
 * No dependencies. Vanilla JS. Auto-mounts when this script loads if either:
 *   - <div id="cs-alerts-root"></div> exists → inserts the card INSIDE it.
 *   - or there is no #cs-alerts-root and a <main class="container"> exists →
 *     inserts the card as a new <section> at the end of <main>.
 *
 * Mounts on both index.html (home) and Analysis/analysis.html alike; both
 * over the relative URL — the analysis page is one level deeper so the JS
 * detects the path and prepends `..` where needed. See `_apiBase()`.
 */

(function () {
  "use strict";

  // --- path detection -----------------------------------------------------

  function _apiBase() {
    // index.html lives at the site root:  "/"
    // analysis.html under /Analysis/:      "../"
    var path = window.location.pathname.toLowerCase();
    if (path.indexOf("/analysis/") === 0 ||
        path.indexOf("/analysis") === path.length - "/analysis".length) {
      return "../";
    }
    return "";
  }

  // --- HTML markup (mirrors weather-alerts.html) --------------------------

  function _buildCardHTML() {
    var s = String.prototype.trim;
    return (
      '<section id="cs-alerts" class="cs-alerts" role="region" aria-labelledby="cs-alerts-title">' +
        '<div class="cs-alerts-card">' +
          '<header class="cs-alerts-header">' +
            '<span class="cs-alerts-eyebrow">Issue #72</span>' +
            '<h2 id="cs-alerts-title">' +
              '<span class="cs-alerts-bell" aria-hidden="true">\uD83D\uDD14</span>' +
              "Get active alerts for your area" +
            "</h2>" +
            '<p class="cs-alerts-sub">' +
              "Climate Shield checks your location twice a day and emails you " +
              "the moment a flood, heatwave, wildfire, cyclone, or drought " +
              "threshold is exceeded. Free, opt-in, one click to stop." +
            "</p>" +
          "</header>" +
          '<form class="cs-alerts-form" id="cs-alerts-form" novalidate autocomplete="on">' +
            '<label class="cs-alerts-row">' +
              '<span class="cs-alerts-label">Email</span>' +
              '<input type="email" name="email" required placeholder="you@example.com" ' +
              'autocomplete="email" maxlength="254" aria-required="true">' +
            "</label>" +
            '<label class="cs-alerts-row">' +
              '<span class="cs-alerts-label">City</span>' +
              '<input type="text" name="city" required placeholder="e.g. Mumbai" ' +
              'autocomplete="address-level2" maxlength="120" aria-required="true">' +
            "</label>" +
            '<div class="cs-alerts-grid-2">' +
              '<label class="cs-alerts-row">' +
                '<span class="cs-alerts-label">State (optional)</span>' +
                '<input type="text" name="state" placeholder="e.g. Maharashtra" maxlength="120">' +
              "</label>" +
              '<label class="cs-alerts-row">' +
                '<span class="cs-alerts-label">Country</span>' +
                '<input type="text" name="country" required placeholder="e.g. India" ' +
                'autocomplete="country-name" maxlength="120" aria-required="true">' +
              "</label>" +
            "</div>" +
            '<button type="submit" class="cs-alerts-submit" id="cs-alerts-submit">' +
              '<span class="cs-alerts-submit-label">Subscribe to active alerts</span>' +
              '<span class="cs-alerts-submit-arrow" aria-hidden="true">\u2192</span>' +
            "</button>" +
            '<p class="cs-alerts-terms">' +
              "By subscribing you agree to receive alert emails about climate " +
              "threats at the chosen location. Unsubscribing is one click in " +
              "any email — your address is never shared or sold." +
            "</p>" +
          "</form>" +
          '<div class="cs-alerts-state" id="cs-alerts-state" hidden></div>' +
          '<aside class="cs-alerts-manage" id="cs-alerts-manage" hidden>' +
            "<h3>Manage your subscription</h3>" +
            "<p>Save this management token to check status or unsubscribe later:</p>" +
            '<code class="cs-alerts-token" id="cs-alerts-token"></code>' +
            '<button type="button" class="cs-alerts-cancel" id="cs-alerts-cancel">Unsubscribe</button>' +
            '<div class="cs-alerts-manage-out" id="cs-alerts-manage-out"></div>' +
          "</aside>" +
        "</div>" +
      "</section>"
    );
  }

  // --- state helpers ------------------------------------------------------

  var EMAIL_RE = /^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$/;

  function _setStateText(el, txt, kind) {
    el.textContent = txt;
    el.className = "cs-alerts-state" + (kind ? " cs-alerts-state--" + kind : "");
    el.hidden = false;
  }

  function _markInvalid(row, invalid) {
    if (invalid) row.classList.add("is-invalid");
    else row.classList.remove("is-invalid");
  }

  function _serialize(form) {
    var obj = {};
    Array.prototype.forEach.call(form.elements, function (el) {
      if (el.name) obj[el.name] = el.value;
    });
    return obj;
  }

  // --- API ----------------------------------------------------------------

  function _apiURL(base, path) {
    return base + path.replace(/^\//, "");
  }

  function _fetchJSON(url, options) {
    options = options || {};
    options.headers = Object.assign(
      { "Content-Type": "application/json", Accept: "application/json" },
      options.headers || {}
    );
    return fetch(url, options).then(function (resp) {
      // Follow same defensive pattern as EduFlow-AI #122: read text first
      // and only try JSON.parse — so a 500-HTML response surfaces a sane
      // error instead of "Unexpected token '<'".
      return resp.text().then(function (txt) {
        if (!txt) return { __ok: resp.ok, __status: resp.status, __body: "" };
        try {
          var data = JSON.parse(txt);
          data.__ok = resp.ok;
          data.__status = resp.status;
          return data;
        } catch (exc) {
          // Looks like HTML/empty — surface a friendly string.
          return {
            __ok: false,
            __status: resp.status,
            success: false,
            message: "Cannot reach the Climate Shield subscription service. " +
                     "Please try again in a moment.",
          };
        }
      });
    });
  }

  // --- main module --------------------------------------------------------

  function WeatherAlerts(root) {
    this.root = root;
    this.base = _apiBase();
    root.innerHTML = _buildCardHTML();
    this.form = root.querySelector("#cs-alerts-form");
    this.submit = root.querySelector("#cs-alerts-submit");
    this.state = root.querySelector("#cs-alerts-state");
    this.manage = root.querySelector("#cs-alerts-manage");
    this.tokenEl = root.querySelector("#cs-alerts-token");
    this.cancelBtn = root.querySelector("#cs-alerts-cancel");
    this.manageOut = root.querySelector("#cs-alerts-manage-out");

    this.currentToken = null;

    this.form.addEventListener("submit", this.onSubmit.bind(this));
    this.cancelBtn.addEventListener("click", this.onUnsubscribe.bind(this));
  }

  WeatherAlerts.prototype.validate = function (data) {
    if (!data.email || !EMAIL_RE.test(data.email) || data.email.length > 254) {
      return { ok: false, field: "email", message: "Please enter a valid email address." };
    }
    if (!data.city || data.city.trim().length === 0 || data.city.length > 120) {
      return { ok: false, field: "city", message: "City is required." };
    }
    if (data.state && data.state.length > 120) {
      return { ok: false, field: "state", message: "State value is too long." };
    }
    if (!data.country || data.country.trim().length === 0 || data.country.length > 120) {
      return { ok: false, field: "country", message: "Country is required." };
    }
    return { ok: true };
  };

  WeatherAlerts.prototype._highlightInvalid = function (fieldName) {
    var inputs = this.form.elements;
    for (var i = 0; i < inputs.length; i++) {
      var row = inputs[i].closest(".cs-alerts-row");
      if (row) _markInvalid(row, inputs[i].name === fieldName);
    }
  };

  WeatherAlerts.prototype.onSubmit = function (ev) {
    ev.preventDefault();
    var self = this;
    var data = _serialize(self.form);
    data.email = (data.email || "").trim().toLowerCase();
    data.city = (data.city || "").trim();
    data.state = (data.state || "").trim();
    data.country = (data.country || "").trim();

    var v = self.validate(data);
    if (!v.ok) {
      _setStateText(self.state, v.message, "err");
      self._highlightInvalid(v.field);
      return;
    }

    self.submit.disabled = true;
    _setStateText(self.state, "Subscribing…", "ok");

    _fetchJSON(_apiURL(self.base, "/subscriptions"), {
      method: "POST",
      body: JSON.stringify(data),
    }).then(function (resp) {
      self.submit.disabled = false;
      if (resp.__ok && resp.success) {
        var sub = resp.subscription || {};
        self.currentToken = sub.management_token;
        _setStateText(
          self.state,
          "Subscription created. We'll email " + sub.email +
          " when threats are detected for " + sub.city + ", " + sub.country + ".",
          "ok"
        );
        self.form.reset();
        self.manage.hidden = false;
        self.tokenEl.textContent = self.currentToken || "";
        self.manageOut.textContent = "";
        self.cancelBtn.disabled = false;
      } else {
        var msg = resp.message || "Subscription failed. Please try again.";
        _setStateText(self.state, msg, "err");
      }
    }).catch(function (exc) {
      self.submit.disabled = false;
      _setStateText(
        self.state,
        "Network error. Please try again in a moment.",
        "err"
      );
    });
  };

  WeatherAlerts.prototype.onUnsubscribe = function (ev) {
    var self = this;
    if (!self.currentToken) { return; }
    self.cancelBtn.disabled = true;
    self.manageOut.textContent = "Unsubscribing…";
    _fetchJSON(
      _apiURL(self.base, "/subscriptions/" + encodeURIComponent(self.currentToken)),
      { method: "DELETE" }
    ).then(function (resp) {
      if (resp.__ok && resp.success) {
        _setStateText(
          self.state,
          "You've unsubscribed. No further alerts will be sent to that address.",
          "ok"
        );
        self.manage.hidden = true;
        self.currentToken = null;
      } else {
        self.cancelBtn.disabled = false;
        self.manageOut.textContent = resp.message || "Unsubscribe failed.";
      }
    }).catch(function (exc) {
      self.cancelBtn.disabled = false;
      self.manageOut.textContent = "Network error — please try again.";
    });
  };

  // --- auto-mount ---------------------------------------------------------

  function _loadCSS(href) {
    if (document.querySelector('link[href="' + href + '"]')) return;
    var link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = href;
    document.head.appendChild(link);
  }

  function mount() {
    var root = document.getElementById("cs-alerts-root");
    var base = _apiBase();
    _loadCSS(base + "weather-alerts/weather-alerts.css");
    if (!root) {
      // Auto-mount at end of <main class="container"> for index.html
      var main = document.querySelector("main.container");
      if (!main) return;
      root = document.createElement("div");
      root.id = "cs-alerts-root";
      main.appendChild(root);
    }
    new WeatherAlerts(root);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mount);
  } else {
    mount();
  }

  // Expose for tests / debugging
  window.WeatherAlerts = WeatherAlerts;
})();
