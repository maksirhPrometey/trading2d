(function () {
  'use strict';

  const sidebar = document.querySelector('[data-catalog-sidebar]');
  const backdrop = document.querySelector('[data-sidebar-backdrop]');
  const openBtn = document.querySelector('[data-sidebar-open]');
  const closeBtn = document.querySelector('[data-sidebar-close]');

  function openSidebar() {
    if (!sidebar || !backdrop) return;
    sidebar.classList.add('is-open');
    backdrop.hidden = false;
    openBtn?.setAttribute('aria-expanded', 'true');
    document.body.style.overflow = 'hidden';
  }

  function closeSidebar() {
    if (!sidebar || !backdrop) return;
    sidebar.classList.remove('is-open');
    backdrop.hidden = true;
    openBtn?.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
  }

  openBtn?.addEventListener('click', openSidebar);
  closeBtn?.addEventListener('click', closeSidebar);
  backdrop?.addEventListener('click', closeSidebar);

  const sortForm = document.querySelector('[data-catalog-sort]');
  const sortSelect = document.getElementById('sort');

  if (sortForm && sortSelect) {
    sortSelect.addEventListener('change', function () {
      sortForm.submit();
    });
  }

  const categoryNav = document.querySelector('[data-category-nav]');
  const searchInput = document.querySelector('[data-category-search]');
  const emptyState = document.querySelector('[data-category-empty]');

  function setHidden(element, hidden) {
    if (!element) return;
    element.hidden = hidden;
  }

  function filterCategories(query) {
    if (!categoryNav) return;

    const normalized = query.trim().toLowerCase();
    const groups = categoryNav.querySelectorAll('[data-category-acc]');
    const leaves = categoryNav.querySelectorAll('[data-category-leaf]');
    const allLink = categoryNav.querySelector('[data-category-all]');
    let visibleCount = 0;

    if (!normalized) {
      groups.forEach(function (group) {
        setHidden(group, false);
        group.querySelectorAll('[data-category-name]').forEach(function (link) {
          const row = link.closest('li');
          setHidden(row || link, false);
        });
        group.open = group.hasAttribute('data-default-open');
      });
      leaves.forEach(function (link) {
        setHidden(link, false);
      });
      setHidden(allLink, false);
      setHidden(emptyState, true);
      return;
    }

    if (allLink) {
      const allVisible = (allLink.dataset.categoryName || '').includes(normalized);
      setHidden(allLink, !allVisible);
      if (allVisible) visibleCount += 1;
    }

    leaves.forEach(function (link) {
      const visible = (link.dataset.categoryName || '').includes(normalized);
      setHidden(link, !visible);
      if (visible) visibleCount += 1;
    });

    groups.forEach(function (group) {
      const groupName = group.dataset.groupName || '';
      const groupMatches = groupName.includes(normalized);
      const links = group.querySelectorAll('[data-category-name]');
      let groupVisible = groupMatches;

      links.forEach(function (link) {
        const match = groupMatches || (link.dataset.categoryName || '').includes(normalized);
        const row = link.closest('li');
        setHidden(row || link, !match);
        if (match) {
          groupVisible = true;
          visibleCount += 1;
        }
      });

      setHidden(group, !groupVisible);
      group.open = groupVisible;
    });

    setHidden(emptyState, visibleCount > 0);
  }

  if (searchInput) {
    searchInput.addEventListener('input', function () {
      filterCategories(searchInput.value);
    });
  }
})();
