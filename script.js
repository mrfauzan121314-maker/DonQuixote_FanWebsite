(function () {
  "use strict";

  var byId = function (id) {
    return document.getElementById(id);
  };

  var all = function (selector, scope) {
    return Array.prototype.slice.call((scope || document).querySelectorAll(selector));
  };

  /* ---------- Nav: scrolled state + mobile menu ---------- */
  function initNav() {
    var nav = byId("nav") || document.querySelector(".nav");
    var toggle = byId("navToggle");
    var menu = byId("navMenu");
    var queued = false;

    if (nav) {
      var onScroll = function () {
        nav.classList.toggle("is-scrolled", window.scrollY > 24);
      };

      window.addEventListener(
        "scroll",
        function () {
          if (queued) return;
          queued = true;
          window.requestAnimationFrame(function () {
            queued = false;
            onScroll();
          });
        },
        { passive: true }
      );
      onScroll();
    }

    if (!toggle || !menu) return;

    var close = function () {
      menu.classList.remove("is-open");
      toggle.setAttribute("aria-expanded", "false");
    };

    toggle.addEventListener("click", function () {
      var open = menu.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });

    menu.addEventListener("click", function (event) {
      if (event.target.closest("a")) close();
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") close();
    });
  }

  /* ---------- Persona tabs (Don Quixote / Sancho) ---------- */
  function initFaces() {
    var tabs = all(".faces__tab");
    var panels = all(".faces__panel");
    if (!tabs.length) return;

    var select = function (face) {
      tabs.forEach(function (tab) {
        var active = tab.dataset.face === face;
        tab.classList.toggle("is-active", active);
        tab.setAttribute("aria-selected", active ? "true" : "false");
      });
      panels.forEach(function (panel) {
        var active = panel.dataset.face === face;
        panel.classList.toggle("is-active", active);
        panel.hidden = !active;
      });
    };

    tabs.forEach(function (tab) {
      tab.addEventListener("click", function () {
        select(tab.dataset.face);
      });

      tab.addEventListener("keydown", function (event) {
        if (event.key !== "ArrowRight" && event.key !== "ArrowLeft") return;
        event.preventDefault();
        var index = tabs.indexOf(tab);
        var next = event.key === "ArrowRight" ? index + 1 : index - 1;
        if (next < 0) next = tabs.length - 1;
        if (next >= tabs.length) next = 0;
        tabs[next].focus();
        select(tabs[next].dataset.face);
      });
    });
  }

  /* ---------- Reveal on scroll ---------- */
  function initReveal() {
    var items = all(".reveal");
    if (!items.length) return;

    if (!("IntersectionObserver" in window)) {
      items.forEach(function (item) {
        item.classList.add("is-visible");
      });
      return;
    }

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.08 }
    );

    items.forEach(function (item) {
      observer.observe(item);
    });
  }

  /* ---------- Active nav link ---------- */
  function initSectionHighlight() {
    var menu = byId("navMenu");
    var sections = all("main section[id]");
    if (!menu || !sections.length || !("IntersectionObserver" in window)) return;

    var links = all('a[href^="#"]', menu);
    if (!links.length) return;

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var hash = "#" + entry.target.id;
          links.forEach(function (link) {
            link.classList.toggle("is-active", link.getAttribute("href") === hash);
          });
        });
      },
      { rootMargin: "-45% 0px -50% 0px" }
    );

    sections.forEach(function (section) {
      observer.observe(section);
    });
  }

  /* ---------- Gallery: one implementation, two configurations ----------
     Handles search, optional filter buttons, optional sort, the live count
     and the "nothing matched" message. */
  function initGallery(config) {
    var cards = all(config.cards);
    var search = byId(config.search);
    var countEl = byId(config.count);
    var emptyEl = byId(config.empty);
    var sortEl = config.sort ? byId(config.sort) : null;
    var grid = document.querySelector(config.grid || ".gallery, .ego-grid");
    if (!cards.length || !search) return;

    var filters = config.filterSelector ? all(config.filterSelector) : [];
    var cardKey = config.cardKey || config.filterKey;
    var activeFilter = "all";

    var textOf = function (card) {
      if (config.haystack) return config.haystack(card).toLowerCase();
      return card.textContent.toLowerCase();
    };

    var fillCounts = function () {
      filters.forEach(function (button) {
        var key = button.dataset[config.filterKey];
        var total =
          key === "all"
            ? cards.length
            : cards.filter(function (card) {
                return card.dataset[cardKey] === key;
              }).length;

        var badge = button.querySelector("span");
        if (!badge) {
          badge = document.createElement("span");
          button.appendChild(badge);
        }
        badge.textContent = total;
      });
    };

    var apply = function () {
      var query = search.value.trim().toLowerCase();
      var visible = 0;

      cards.forEach(function (card) {
        var inFilter = activeFilter === "all" || card.dataset[cardKey] === activeFilter;
        var matches = !query || textOf(card).indexOf(query) !== -1;
        var show = inFilter && matches;

        card.hidden = !show;
        if (show) {
          card.classList.add("is-visible");
          visible += 1;
        }
      });

      if (countEl) {
        countEl.textContent =
          "Menampilkan " + visible + " dari " + cards.length + " " + config.label;
      }
      if (emptyEl) emptyEl.hidden = visible !== 0;
    };

    var sortCards = function (mode) {
      if (!grid || !sortEl) return;

      var ordered = cards.slice();
      if (mode === "newest" || mode === "oldest") {
        var direction = mode === "newest" ? -1 : 1;
        ordered.sort(function (a, b) {
          return direction * a.dataset.release.localeCompare(b.dataset.release);
        });
      } else if (mode === "cost-desc" || mode === "cost-asc") {
        var sign = mode === "cost-desc" ? -1 : 1;
        ordered.sort(function (a, b) {
          return sign * (Number(a.dataset.cost) - Number(b.dataset.cost));
        });
      }

      ordered.forEach(function (card) {
        grid.appendChild(card);
      });
    };

    filters.forEach(function (button) {
      button.addEventListener("click", function () {
        activeFilter = button.dataset[config.filterKey];
        filters.forEach(function (other) {
          var active = other === button;
          other.classList.toggle("is-active", active);
          other.setAttribute("aria-pressed", active ? "true" : "false");
        });
        apply();
      });
    });

    search.addEventListener("input", apply);

    if (sortEl) {
      sortEl.addEventListener("change", function () {
        sortCards(sortEl.value);
      });
    }

    fillCounts();
    apply();
  }

  initNav();
  initFaces();
  initReveal();
  initSectionHighlight();

  initGallery({
    cards: ".idcard",
    search: "identitySearch",
    count: "identityCount",
    empty: "galleryEmpty",
    filterSelector: ".filter[data-filter]",
    filterKey: "filter",
    cardKey: "group",
    grid: ".gallery",
    label: "Identity",
    haystack: function (card) {
      var body = card.querySelector(".idcard__body");
      return (card.dataset.search || "") + " " + (body ? body.textContent : "");
    },
  });

  initGallery({
    cards: ".egocard",
    search: "egoSearch",
    count: "egoCount",
    empty: "egoEmpty",
    filterSelector: ".egofilter",
    filterKey: "risk",
    sort: "egoSort",
    grid: ".ego-grid",
    label: "E.G.O",
  });
})();
