(function () {
  'use strict';

  const drawer = document.querySelector('[data-cart-drawer]');
  const backdrop = document.querySelector('[data-cart-backdrop]');
  const bodyEl = document.querySelector('[data-cart-drawer-body]');
  const countEl = document.getElementById('cart-count');
  const totalEl = document.querySelector('[data-cart-total]');
  if (!drawer || !backdrop) return;

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function setOpen(open) {
    drawer.classList.toggle('is-open', open);
    backdrop.classList.toggle('is-open', open);
    backdrop.hidden = !open;
    drawer.setAttribute('aria-hidden', open ? 'false' : 'true');
    document.body.classList.toggle('cart-drawer-open', open);
    if (open) {
      const closeBtn = drawer.querySelector('[data-cart-close]');
      closeBtn && closeBtn.focus();
    }
  }

  function csrfToken() {
    const input = document.querySelector('[name=csrfmiddlewaretoken]');
    return input ? input.value : '';
  }

  function refreshDrawer() {
    const drawerUrl = document.documentElement.dataset.cartDrawerUrl || '/cart/?fragment=drawer';
    return fetch(drawerUrl, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
      credentials: 'same-origin',
    }).then(function (response) {
      if (!response.ok) return;
      return response.text();
    }).then(function (html) {
      if (html && bodyEl) bodyEl.innerHTML = html;
    });
  }

  function updateCount(value) {
    if (countEl && typeof value !== 'undefined') {
      countEl.textContent = String(value);
    }
  }

  document.addEventListener('click', function (event) {
    const opener = event.target.closest('[data-cart-open]');
    if (opener) {
      event.preventDefault();
      setOpen(true);
      return;
    }
    if (event.target.closest('[data-cart-close]') || event.target === backdrop) {
      setOpen(false);
    }
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && drawer.classList.contains('is-open')) {
      setOpen(false);
    }
  });

  document.addEventListener('submit', function (event) {
    const form = event.target;
    if (!(form instanceof HTMLFormElement)) return;
    if (!form.classList.contains('card-add-to-cart-form') && form.id !== 'add-to-cart-form') {
      return;
    }
    event.preventDefault();
    const data = new FormData(form);
    fetch(form.action, {
      method: 'POST',
      body: data,
      credentials: 'same-origin',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': csrfToken(),
      },
    }).then(function (response) {
      if (!response.ok) throw new Error('cart-add-failed');
      return response.json();
    }).then(function (payload) {
      updateCount(payload.cart_items_count);
      if (totalEl && payload.total_price) {
        const uah = document.documentElement.dataset.uah || 'грн';
        totalEl.textContent = Number(payload.total_price).toFixed(0) + ' ' + uah;
      }
      return refreshDrawer();
    }).then(function () {
      setOpen(true);
    }).catch(function () {
      form.submit();
    });
  });

  if (reduceMotion) {
    drawer.style.transition = 'none';
    backdrop.style.transition = 'none';
  }
})();
