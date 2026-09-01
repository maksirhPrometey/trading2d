(function () {
  'use strict';

  const langSelect = document.querySelector('[data-lang-select]');
  if (langSelect && langSelect.form) {
    langSelect.addEventListener('change', function () {
      langSelect.form.submit();
    });
  }
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
