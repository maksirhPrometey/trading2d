(function () {
  'use strict';

  const mainImage = document.getElementById('product-main-image');
  const qtyInput = document.getElementById('qty-input');
  const qtyMinus = document.getElementById('qty-minus');
  const qtyPlus = document.getElementById('qty-plus');
  const thumbs = document.querySelectorAll('[data-gallery-thumb]');

  function dialogEl() {
    return document.querySelector('[data-product-lightbox]');
  }

  function lightboxImageEl() {
    return document.querySelector('[data-lightbox-image]');
  }

  function getSources() {
    const fromThumbs = Array.from(document.querySelectorAll('[data-gallery-thumb]'))
      .map(function (thumb) { return thumb.dataset.src; })
      .filter(Boolean);
    if (fromThumbs.length) {
      return fromThumbs;
    }
    if (mainImage && mainImage.tagName === 'IMG') {
      return [mainImage.currentSrc || mainImage.src];
    }
    return [];
  }

  function currentIndex(sources) {
    if (!mainImage || mainImage.tagName !== 'IMG') {
      return 0;
    }
    const current = mainImage.currentSrc || mainImage.src;
    const index = sources.findIndex(function (src) {
      return current.indexOf(src) !== -1;
    });
    return index >= 0 ? index : 0;
  }

  function setMainImage(src) {
    if (!mainImage || mainImage.tagName !== 'IMG' || !src) {
      return;
    }
    thumbs.forEach(function (item) {
      item.classList.toggle('active', item.dataset.src === src);
    });
    if (mainImage.getAttribute('src') === src || mainImage.src.indexOf(src) !== -1) {
      return;
    }
    mainImage.classList.add('is-switching');
    window.setTimeout(function () {
      mainImage.src = src;
      mainImage.classList.remove('is-switching');
    }, 180);
  }

  function renderLightbox(index) {
    const sources = getSources();
    const image = lightboxImageEl();
    const counter = document.querySelector('[data-lightbox-counter]');
    const prevBtn = document.querySelector('[data-lightbox-prev]');
    const nextBtn = document.querySelector('[data-lightbox-next]');
    if (!sources.length || !image) {
      return;
    }
    const safeIndex = (index + sources.length) % sources.length;
    image.src = sources[safeIndex];
    image.alt = mainImage && mainImage.alt ? mainImage.alt : '';
    if (counter) {
      counter.textContent = (safeIndex + 1) + ' / ' + sources.length;
    }
    const many = sources.length > 1;
    if (prevBtn) prevBtn.hidden = !many;
    if (nextBtn) nextBtn.hidden = !many;
    image.dataset.index = String(safeIndex);
    setMainImage(sources[safeIndex]);
  }

  function openLightbox(index) {
    const dialog = dialogEl();
    if (!dialog || typeof dialog.showModal !== 'function') {
      return;
    }
    renderLightbox(index);
    if (!dialog.open) {
      dialog.showModal();
    }
  }

  function closeLightbox() {
    const dialog = dialogEl();
    if (dialog && dialog.open) {
      dialog.close();
    }
  }

  function step(delta) {
    const image = lightboxImageEl();
    const index = Number(image && image.dataset.index) || 0;
    renderLightbox(index + delta);
  }

  thumbs.forEach(function (thumb) {
    thumb.addEventListener('click', function () {
      setMainImage(thumb.dataset.src);
    });
  });

  document.addEventListener('click', function (event) {
    if (event.target.closest('[data-lightbox-open]')) {
      openLightbox(currentIndex(getSources()));
      return;
    }
    if (event.target.closest('[data-lightbox-prev]')) {
      step(-1);
      return;
    }
    if (event.target.closest('[data-lightbox-next]')) {
      step(1);
      return;
    }
    if (event.target.closest('[data-lightbox-close]')) {
      closeLightbox();
      return;
    }
    const dialog = dialogEl();
    if (dialog && dialog.open && event.target === dialog) {
      closeLightbox();
    }
  });

  document.addEventListener('keydown', function (event) {
    const dialog = dialogEl();
    if (!dialog || !dialog.open) {
      return;
    }
    if (event.key === 'Escape') {
      closeLightbox();
      return;
    }
    if (event.key === 'ArrowLeft') {
      event.preventDefault();
      step(-1);
    }
    if (event.key === 'ArrowRight') {
      event.preventDefault();
      step(1);
    }
  });

  var touchStartX = 0;
  document.addEventListener('touchstart', function (event) {
    const dialog = dialogEl();
    if (!dialog || !dialog.open) {
      return;
    }
    touchStartX = event.changedTouches[0].clientX;
  }, { passive: true });

  document.addEventListener('touchend', function (event) {
    const dialog = dialogEl();
    if (!dialog || !dialog.open || event.target.closest('.lightbox-btn')) {
      return;
    }
    var dx = event.changedTouches[0].clientX - touchStartX;
    if (dx > 48) {
      step(-1);
    } else if (dx < -48) {
      step(1);
    }
  }, { passive: true });

  if (qtyInput && qtyMinus && qtyPlus) {
    qtyMinus.addEventListener('click', function () {
      qtyInput.value = String(Math.max(1, parseInt(qtyInput.value || '1', 10) - 1));
    });

    qtyPlus.addEventListener('click', function () {
      const max = parseInt(qtyInput.max || '99', 10);
      qtyInput.value = String(Math.min(max, parseInt(qtyInput.value || '1', 10) + 1));
    });
  }

  function showShareToast(message) {
    const toast = document.createElement('div');
    toast.className = 'share-toast';
    toast.textContent = message;
    toast.setAttribute('role', 'status');
    document.body.appendChild(toast);
    window.requestAnimationFrame(function () {
      toast.classList.add('is-visible');
    });
    window.setTimeout(function () {
      toast.classList.remove('is-visible');
      window.setTimeout(function () {
        toast.remove();
      }, 250);
    }, 2200);
  }

  function flashShareLabel(btn, text) {
    const label = btn.querySelector('[data-share-label]');
    if (!label) return;
    const original = label.textContent;
    label.textContent = text;
    window.setTimeout(function () {
      label.textContent = original;
    }, 2000);
  }

  document.addEventListener('click', function (event) {
    const btn = event.target.closest('[data-share-button]');
    if (!btn) return;

    const url = btn.dataset.shareUrl || window.location.href;
    const title = btn.dataset.shareTitle || document.title;

    if (navigator.share) {
      navigator.share({ title: title, url: url }).catch(function () {
        /* користувач закрив системне меню "Поділитись" – нічого не робимо */
      });
      return;
    }

    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(function () {
        flashShareLabel(btn, document.documentElement.dataset.shareCopied || '');
        showShareToast(document.documentElement.dataset.shareOk || '');
      }).catch(function () {
        showShareToast(document.documentElement.dataset.shareFail || '');
      });
      return;
    }

    window.prompt(document.documentElement.dataset.sharePrompt || '', url);
  });
})();
