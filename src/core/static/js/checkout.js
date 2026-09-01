/* Автопідбір міста/відділення Нової Пошти для чекауту. Якщо
   NOVA_POSHTA_API_KEY не налаштований на бекенді, ендпоінти повернуть
   {results: [], error: ...} — поля лишаються звичайними текстовими полями. */
(function () {
  'use strict';

  const cityInput = document.getElementById('np-city-input');
  const cityRefInput = document.querySelector('input[name="np_city_ref"]');
  const cityResults = document.querySelector('[data-np-city-results]');

  const warehouseInput = document.getElementById('np-warehouse-input');
  const warehouseRefInput = document.querySelector('input[name="np_warehouse_ref"]');
  const warehouseResults = document.querySelector('[data-np-warehouse-results]');

  let debounceTimer = null;

  function debounce(fn, delay) {
    return function (...args) {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(function () {
        fn.apply(null, args);
      }, delay);
    };
  }

  function renderResults(container, items, onSelect) {
    if (!container) return;
    if (!items.length) {
      container.hidden = true;
      container.innerHTML = '';
      return;
    }
    container.hidden = false;
    container.innerHTML = items.map(function (item, index) {
      return '<li><button type="button" class="category-child-link" data-index="' + index + '">' + item.name + '</button></li>';
    }).join('');

    container.querySelectorAll('button[data-index]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        onSelect(items[Number(btn.dataset.index)]);
        container.hidden = true;
        container.innerHTML = '';
      });
    });
  }

  if (cityInput) {
    cityInput.addEventListener('input', debounce(function () {
      const query = cityInput.value.trim();
      if (query.length < 2) {
        renderResults(cityResults, [], function () {});
        return;
      }
      const citiesUrl = document.documentElement.dataset.npCitiesUrl || '/orders/nova-poshta/cities/';
      fetch(citiesUrl + '?q=' + encodeURIComponent(query))
        .then(function (res) { return res.json(); })
        .then(function (data) {
          renderResults(cityResults, data.results || [], function (item) {
            cityInput.value = item.name;
            if (cityRefInput) cityRefInput.value = item.ref;
            if (warehouseInput) {
              warehouseInput.value = '';
              warehouseInput.disabled = false;
            }
          });
        })
        .catch(function () { /* мережева помилка — поле лишається звичайним текстовим */ });
    }, 300));
  }

  if (warehouseInput) {
    warehouseInput.addEventListener('input', debounce(function () {
      const cityRef = cityRefInput ? cityRefInput.value : '';
      if (!cityRef) return;
      const query = warehouseInput.value.trim().toLowerCase();
      const warehousesUrl = document.documentElement.dataset.npWarehousesUrl || '/orders/nova-poshta/warehouses/';
      fetch(warehousesUrl + '?city_ref=' + encodeURIComponent(cityRef))
        .then(function (res) { return res.json(); })
        .then(function (data) {
          const items = (data.results || []).filter(function (item) {
            return !query || item.name.toLowerCase().includes(query);
          });
          renderResults(warehouseResults, items, function (item) {
            warehouseInput.value = item.name;
            if (warehouseRefInput) warehouseRefInput.value = item.ref;
          });
        })
        .catch(function () { /* мережева помилка — поле лишається звичайним текстовим */ });
    }, 300));
  }
})();
