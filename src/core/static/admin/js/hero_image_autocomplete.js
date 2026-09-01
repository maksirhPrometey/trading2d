(function () {
  function getJQuery() {
    return window.django && window.django.jQuery;
  }

  function formatOption(item) {
    var $ = getJQuery();
    if (item.loading) {
      return item.text;
    }

    var imageUrl = item.image_url || item.imageUrl;
    var $wrapper = $('<span class="hero-image-option"></span>');
    if (imageUrl) {
      $('<img>', {
        src: imageUrl,
        alt: '',
        class: 'hero-image-option__thumb',
      }).appendTo($wrapper);
    }
    $('<span class="hero-image-option__text"></span>').text(item.text).appendTo($wrapper);
    return $wrapper;
  }

  function initHeroImagePreview() {
    var $ = getJQuery();
    if (!$) {
      return;
    }

    var $field = $('#id_hero_image');
    if (!$field.length) {
      return;
    }

    if ($field.hasClass('select2-hidden-accessible')) {
      $field.select2('destroy');
    }

    var element = $field.get(0);

    // Select2 читає повний item лише з jQuery-даних "data" на <option>
    // (Utils.GetData шукає саме ключ "data"), звичайні data-* атрибути
    // самі по собі не потрапляють у templateSelection/templateResult.
    // Тож вручну кладемо image_url з data-image-url у це сховище для
    // вже вибраної опції — інакше закритий select лишиться без мініатюри.
    $(element)
      .find('option[data-image-url]')
      .each(function () {
        $(this).data('data', {
          id: this.value,
          text: this.textContent,
          image_url: this.dataset.imageUrl,
          selected: this.selected,
        });
      });

    $field.select2({
      templateResult: formatOption,
      templateSelection: formatOption,
      ajax: {
        data: function (params) {
          return {
            term: params.term,
            page: params.page,
            app_label: element.dataset.appLabel,
            model_name: element.dataset.modelName,
            field_name: element.dataset.fieldName,
          };
        },
      },
    });
  }

  window.addEventListener('load', initHeroImagePreview);
})();
