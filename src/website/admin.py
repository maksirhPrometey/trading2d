from django.contrib import admin
from django.contrib.admin.views.autocomplete import AutocompleteJsonView
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display

from src.products.models import Gallery
from src.website.admin_tinymce import TinyMCEAdminMixin
from src.website.models import (
    ContactPage,
    HomeShowcaseItem,
    MainPage,
    Page,
    SiteSettings,
)
from src.website.pages import SYSTEM_PAGES, SYSTEM_PAGES_BY_SLUG
from src.website import admin_auth  # noqa: F401


class ThumbnailAutocompleteJsonView(AutocompleteJsonView):
    """Додає image_url та назву товару у відповідь автодоповнення для Gallery,
    щоб select2 міг показати міні-фото і шукати по назві товару."""

    def serialize_result(self, obj, to_field_name):
        result = super().serialize_result(obj, to_field_name)
        if isinstance(obj, Gallery):
            if obj.image:
                result['image_url'] = obj.image.url
            product_names = ', '.join(p.name for p in obj.products.all()[:3])
            if product_names:
                result['text'] = product_names
        return result


# Стандартний admin.site.autocomplete_view не дає per-модельного гачка для
# розширення JSON, тож підміняємо його один раз на in'єктовану версію, яка
# додатково повертає image_url для Gallery (інші моделі — без змін).
admin.site.autocomplete_view = ThumbnailAutocompleteJsonView.as_view(admin_site=admin.site)


class SingletonAdmin(ModelAdmin):
    def has_add_permission(self, request):
        return not self.model.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        defaults = {}
        if hasattr(self.model, 'singleton_defaults'):
            defaults = self.model.singleton_defaults()
        obj, _ = self.model.objects.get_or_create(pk=1, defaults=defaults)
        return HttpResponseRedirect(
            reverse(
                f'admin:{self.opts.app_label}_{self.opts.model_name}_change',
                args=[obj.pk],
            )
        )


class ShowcaseSlotFormSet(BaseInlineFormSet):
    slot = None
    prefix_name = None

    @classmethod
    def get_default_prefix(cls):
        return cls.prefix_name or super().get_default_prefix()

    def clean(self):
        super().clean()
        if any(self.errors):
            return
        seen = []
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get('DELETE'):
                continue
            product = form.cleaned_data.get('product')
            if product is None:
                continue
            if product in seen:
                raise ValidationError(
                    'Той самий товар не можна додати двічі в один блок.'
                )
            seen.append(product)

    def save_new(self, form, commit=True):
        obj = super().save_new(form, commit=False)
        obj.slot = self.slot
        if commit:
            obj.save()
        return obj

    def save_existing(self, form, instance, commit=True):
        obj = super().save_existing(form, instance, commit=False)
        obj.slot = self.slot
        if commit:
            obj.save()
        return obj


class BestsellerFormSet(ShowcaseSlotFormSet):
    slot = HomeShowcaseItem.Slot.BESTSELLER
    prefix_name = 'bestsellers'


class NewArrivalFormSet(ShowcaseSlotFormSet):
    slot = HomeShowcaseItem.Slot.NEW_ARRIVAL
    prefix_name = 'new_arrivals'


class ShowcaseSlotInline(TabularInline):
    model = HomeShowcaseItem
    extra = 0
    max_num = 8
    tab = True
    autocomplete_fields = ('product',)
    fields = ('product', 'order')
    ordering = ('order', 'pk')
    slot = None

    def get_queryset(self, request):
        return super().get_queryset(request).filter(slot=self.slot).select_related('product')


class BestsellerInline(ShowcaseSlotInline):
    formset = BestsellerFormSet
    slot = HomeShowcaseItem.Slot.BESTSELLER
    verbose_name = 'Хіт продажу'
    verbose_name_plural = 'Хіти продажу'


class NewArrivalInline(ShowcaseSlotInline):
    formset = NewArrivalFormSet
    slot = HomeShowcaseItem.Slot.NEW_ARRIVAL
    verbose_name = 'Новинка'
    verbose_name_plural = 'Новинки'


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonAdmin):
    fieldsets = (
        ('Основне', {'fields': ('site_name',)}),
        ('Брендинг', {'fields': ('site_logo', 'logo_preview', 'site_favicon', 'favicon_preview')}),
    )
    readonly_fields = ('logo_preview', 'favicon_preview')

    def changelist_view(self, request, extra_context=None):
        obj, _ = SiteSettings.objects.get_or_create(
            pk=1,
            defaults={'site_name': 'TRADING 2D'},
        )
        return HttpResponseRedirect(
            reverse('admin:website_sitesettings_change', args=[obj.pk])
        )

    @display(description='Логотип', image=True)
    def logo_preview(self, obj):
        if obj.pk and obj.site_logo:
            return obj.site_logo.url
        return None

    @display(description='Favicon', image=True)
    def favicon_preview(self, obj):
        if obj.pk and obj.site_favicon:
            return obj.site_favicon.url
        return None


@admin.register(MainPage)
class MainPageAdmin(SingletonAdmin):
    inlines = (BestsellerInline, NewArrivalInline)
    autocomplete_fields = ('hero_image',)
    fieldsets = (
        ('Контент', {'fields': ('title', 'description')}),
        (
            'Переклади',
            {
                'classes': ('collapse',),
                'fields': ('title_ru', 'title_en', 'description_ru', 'description_en'),
            },
        ),
        (
            'Банер',
            {
                'fields': ('hero_image', 'hero_image_preview', 'banner_image', 'banner_preview'),
                'description': (
                    'banner_image — фон усього банера на головній. hero_image — окреме фото товару '
                    'праворуч; шукайте за назвою товару. Якщо не обрано — підбирається автоматично '
                    'з хітів/новинок.'
                ),
            },
        ),
    )
    readonly_fields = ('hero_image_preview', 'banner_preview')
    warn_unsaved_form = True

    class Media:
        js = ('admin/js/hero_image_autocomplete.js',)
        css = {'all': ('admin/css/hero_image_autocomplete.css',)}

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'hero_image':
            # Пробрасуємо image_url у data-атрибут вже вибраного <option>, щоб
            # JS міг показати міні-фото і для поточного значення (не тільки
            # для варіантів, підвантажених через AJAX-пошук).
            original_create_option = formfield.widget.create_option

            def create_option(name, value, label, selected, index, subindex=None, attrs=None):
                option = original_create_option(name, value, label, selected, index, subindex, attrs)
                if value:
                    gallery = Gallery.objects.filter(pk=value).first()
                    if gallery and gallery.image:
                        option['attrs']['data-image-url'] = gallery.image.url
                return option

            formfield.widget.create_option = create_option
        return formfield

    @display(description='Превʼю фото товару', image=True)
    def hero_image_preview(self, obj):
        if obj.pk and obj.hero_image and obj.hero_image.image:
            return obj.hero_image.image.url
        return None

    @display(description='Банер', image=True)
    def banner_preview(self, obj):
        if obj.pk and obj.banner_image:
            return obj.banner_image.url
        return None


@admin.register(ContactPage)
class ContactPageAdmin(TinyMCEAdminMixin, SingletonAdmin):
    tinymce_fields = ('description', 'description_ru', 'description_en')
    fieldsets = (
        ('Контент', {'fields': ('title', 'description', 'image', 'image_preview')}),
        (
            'Переклади',
            {
                'classes': ('collapse',),
                'fields': (
                    'title_ru',
                    'title_en',
                    'description_ru',
                    'description_en',
                    'address_ru',
                    'address_en',
                ),
            },
        ),
        ('Контакти', {'fields': ('email', 'phone', 'address')}),
    )
    readonly_fields = ('image_preview',)
    warn_unsaved_form = True

    @display(description='Зображення', image=True)
    def image_preview(self, obj):
        if obj.pk and obj.image:
            return obj.image.url
        return None


@admin.register(Page)
class PageAdmin(TinyMCEAdminMixin, ModelAdmin):
    tinymce_fields = ('description', 'description_ru', 'description_en')
    list_display = ('title', 'slug')
    readonly_fields = ('slug',)
    search_fields = ('title', 'title_ru', 'title_en')
    warn_unsaved_form = True
    fieldsets = (
        ('Сторінка', {'fields': ('title', 'slug')}),
        ('Контент', {'fields': ('description',)}),
        (
            'Переклади',
            {
                'classes': ('collapse',),
                'fields': ('title_ru', 'title_en', 'description_ru', 'description_en'),
            },
        ),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop('delete_selected', None)
        return actions

    def get_urls(self):
        def make_view(slug):
            def view(request, extra_context=None):
                return self.system_page_view(request, slug)

            view.__name__ = f'page_{slug}_view'
            return self.admin_site.admin_view(view)

        custom = [
            path(f'{spec.slug}/', make_view(spec.slug), name=f'website_page_{spec.slug}')
            for spec in SYSTEM_PAGES
        ]
        return custom + super().get_urls()

    def system_page_view(self, request, slug):
        spec = SYSTEM_PAGES_BY_SLUG[slug]
        obj = Page.load(slug)
        extra = {'title': spec.admin_title}
        return self.change_view(request, str(obj.pk), extra_context=extra)

    def response_post_save_change(self, request, obj):
        return HttpResponseRedirect(reverse(f'admin:website_page_{obj.slug}'))

    def response_change(self, request, obj):
        if '_continue' in request.POST:
            return HttpResponseRedirect(reverse(f'admin:website_page_{obj.slug}'))
        return super().response_change(request, obj)

    def changelist_view(self, request, extra_context=None):
        first = SYSTEM_PAGES[0]
        return HttpResponseRedirect(reverse(f'admin:website_page_{first.slug}'))
