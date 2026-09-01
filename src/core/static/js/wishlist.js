(function () {
  'use strict';

  const root = document.documentElement;
  const countEl = document.getElementById('wishlist-count');
  const toggleTpl = root.dataset.wishlistToggleTpl || '/wishlist/toggle/__SLUG__/';
  const catalogUrl = root.dataset.catalogUrl || '/catalog/';
  const catalogCta = root.dataset.catalogCta || '';
  const emptyText = root.dataset.wishlistEmpty || '';
  const labelIn = root.dataset.wishlistIn || '';
  const labelOut = root.dataset.wishlistOut || '';

  function getCookie(name) {
    const match = document.cookie.match('(^|;\\s*)' + name + '=([^;]*)');
    return match ? decodeURIComponent(match[2]) : '';
  }

  function updateCount(value) {
    if (countEl && typeof value !== 'undefined') {
      countEl.textContent = String(value);
    }
  }

  function showEmptyStateIfNeeded() {
    const page = document.querySelector('[data-wishlist-page]');
    if (!page || page.querySelector('[data-wishlist-item]')) {
      return;
    }
    page.innerHTML =
      '<div class="cart-empty" data-wishlist-empty>' +
      '<p>' + emptyText + '</p>' +
      '<a href="' + catalogUrl + '" class="btn btn-primary">' + catalogCta + '</a>' +
      '</div>';
  }

  function setButtonState(btn, active) {
    btn.classList.toggle('is-active', active);
    btn.setAttribute('aria-pressed', active ? 'true' : 'false');
    const label = btn.querySelector('[data-wishlist-label]');
    if (label) {
      label.textContent = active ? labelIn : labelOut;
    }
  }

  document.addEventListener('click', function (event) {
    const btn = event.target.closest('[data-wishlist-toggle]');
    if (!btn) return;
    event.preventDefault();
    if (btn.dataset.loading === '1') return;

    const slug = btn.dataset.productSlug;
    if (!slug) return;

    btn.dataset.loading = '1';

    fetch(toggleTpl.replace('__SLUG__', slug), {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': getCookie('csrftoken'),
      },
    }).then(function (response) {
      if (!response.ok) throw new Error('wishlist-toggle-failed');
      return response.json();
    }).then(function (payload) {
      updateCount(payload.count);
      document
        .querySelectorAll('[data-wishlist-toggle][data-product-slug="' + slug + '"]')
        .forEach(function (el) {
          setButtonState(el, payload.in_wishlist);
        });

      if (!payload.in_wishlist) {
        const wishlistCard = btn.closest('[data-wishlist-item]');
        if (wishlistCard) {
          wishlistCard.remove();
          showEmptyStateIfNeeded();
        }
      }
    }).catch(function () {
      /* мовчки лишаємо кнопку в попередньому стані – мережева помилка
         не повинна ламати навігацію по сторінці */
    }).finally(function () {
      btn.dataset.loading = '0';
    });
  });
})();
