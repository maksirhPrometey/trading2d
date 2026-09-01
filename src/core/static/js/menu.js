(function () {
  'use strict';

  const menuToggle = document.getElementById('menu-toggle');
  const mobileMenu = document.getElementById('mobile-menu');

  if (!menuToggle || !mobileMenu) return;

  menuToggle.addEventListener('click', function () {
    const isOpen = mobileMenu.classList.toggle('active');
    menuToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
  });

  mobileMenu.querySelectorAll('a').forEach(function (link) {
    link.addEventListener('click', function () {
      mobileMenu.classList.remove('active');
      menuToggle.setAttribute('aria-expanded', 'false');
    });
  });
})();
