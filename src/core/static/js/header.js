(function () {
  'use strict';

  const root = document.querySelector('[data-lang-menu]');
  if (!root) return;

  const toggle = root.querySelector('.lang-toggle');
  const panel = root.querySelector('.lang-menu');
  if (!toggle || !panel) return;

  function setOpen(open) {
    root.classList.toggle('is-open', open);
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    panel.hidden = !open;
  }

  toggle.addEventListener('click', function (event) {
    event.preventDefault();
    event.stopPropagation();
    setOpen(panel.hidden);
  });

  document.addEventListener('click', function (event) {
    if (!root.classList.contains('is-open')) return;
    if (root.contains(event.target)) return;
    setOpen(false);
  });

  document.addEventListener('keydown', function (event) {
    if (event.key !== 'Escape' || !root.classList.contains('is-open')) return;
    setOpen(false);
    toggle.focus();
  });
})();

/* RULE-30: dual-row sticky header — другий рядок навігації згортається
   при скролі вниз і повертається при скролі вгору. Два різні пороги
   (96 / 24px) створюють hysteresis і прибирають "миготіння" біля межі. */
(function () {
  'use strict';

  const header = document.querySelector('.site-header');
  if (!header || !window.matchMedia('(min-width: 900px)').matches) {
    return;
  }

  const COLLAPSE_AT = 96;
  const EXPAND_AT = 24;
  let ticking = false;

  function updateHeaderState() {
    const scrollY = window.scrollY || window.pageYOffset;

    if (scrollY > COLLAPSE_AT) {
      header.classList.add('header--compact');
    } else if (scrollY < EXPAND_AT) {
      header.classList.remove('header--compact');
    }

    ticking = false;
  }

  window.addEventListener('scroll', function () {
    if (!ticking) {
      window.requestAnimationFrame(updateHeaderState);
      ticking = true;
    }
  }, { passive: true });
})();
