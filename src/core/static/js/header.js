(function () {
  'use strict';

  const menu = document.querySelector('[data-lang-menu]');
  if (!menu) return;

  document.addEventListener('click', function (event) {
    if (!menu.hasAttribute('open')) return;
    if (menu.contains(event.target)) return;
    menu.removeAttribute('open');
  });

  document.addEventListener('keydown', function (event) {
    if (event.key !== 'Escape' || !menu.hasAttribute('open')) return;
    menu.removeAttribute('open');
    const toggle = menu.querySelector('.lang-toggle');
    if (toggle) toggle.focus();
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
