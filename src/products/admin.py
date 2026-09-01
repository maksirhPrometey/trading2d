from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import (
    BooleanRadioFilter,
    RangeNumericFilter,
    RelatedDropdownFilter,
)
from unfold.decorators import display

from src.products.models import Brand, Category, Gallery, Product, ProductAttribute
from src.website.admin_tinymce import TinyMCEAdminMixin


class ProductAttributeInline(TabularInline):
    model = ProductAttribute
    extra = 0
    tab = True
    fields = ('name', 'name_ru', 'name_en', 'value', 'value_ru', 'value_en', 'order')


@admin.register(Gallery)
class GalleryAdmin(ModelAdmin):
    list_display = ('image_preview', 'source_url')
    search_fields = ('products__name', 'image', 'source_url')
    readonly_fields = ('image_preview',)
    fields = ('image', 'image_preview', 'source_url')

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('products')

    @display(description='Превʼю', image=True)
    def image_preview(self, obj):
        if obj.pk and obj.image:
            return obj.image.url
        return None


@admin.register(Product)
class ProductAdmin(TinyMCEAdminMixin, ModelAdmin):
    tinymce_fields = ('description', 'description_ru', 'description_en')
    list_display = (
        'image_preview',
        'name',
        'sku',
        'brand',
        'category',
        'price',
        'in_stock_badge',
        'is_bestseller',
        'is_new',
    )
    list_filter = (
        ('category', RelatedDropdownFilter),
        ('brand', RelatedDropdownFilter),
        ('price', RangeNumericFilter),
        ('in_stock', BooleanRadioFilter),
        'is_bestseller',
        'is_new',
    )
    list_filter_submit = True
    search_fields = ('name', 'sku', 'slug', 'vendor_code', 'barcode', 'external_id')
    list_select_related = ('category', 'brand')
    filter_horizontal = ('images',)
    inlines = [ProductAttributeInline]
    readonly_fields = ('created_at',)
    warn_unsaved_form = True
    list_per_page = 25
    fieldsets = (
        ('Основне', {'fields': ('name', 'slug', 'sku', 'description')}),
        (
            'Переклади',
            {
                'classes': ('collapse',),
                'fields': (
                    'name_ru',
                    'name_en',
                    'description_ru',
                    'description_en',
                    'meta_title',
                    'meta_title_ru',
                    'meta_title_en',
                    'meta_description',
                    'meta_description_ru',
                    'meta_description_en',
                ),
            },
        ),
        ('Ціна та склад', {'fields': ('price', 'old_price', 'in_stock', 'stock_quantity')}),
        ('Вітрина', {'fields': ('is_bestseller', 'is_new', 'category', 'brand', 'images')}),
        (
            'Постачальник',
            {
                'classes': ('collapse',),
                'fields': ('external_id', 'vendor_code', 'barcode', 'source_url', 'created_at'),
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('images')

    @display(description='Фото', image=True)
    def image_preview(self, obj):
        image = obj.primary_image
        if image and image.image:
            return image.image.url
        return None

    @display(description='Наявність', boolean=True)
    def in_stock_badge(self, obj):
        return obj.in_stock


@admin.register(Category)
class CategoryAdmin(TinyMCEAdminMixin, ModelAdmin):
    tinymce_fields = ('description', 'description_ru', 'description_en')
    list_display = ('image_preview', 'name', 'parent', 'external_id')
    list_filter = (('parent', RelatedDropdownFilter),)
    search_fields = ('name', 'external_id')
    list_select_related = ('parent',)
    readonly_fields = ('image_preview',)
    fields = (
        'name',
        'name_ru',
        'name_en',
        'description',
        'description_ru',
        'description_en',
        'parent',
        'image',
        'image_preview',
        'external_id',
    )

    @display(description='Фото', image=True)
    def image_preview(self, obj):
        if obj.pk and obj.image:
            return obj.image.url
        return None


@admin.register(Brand)
class BrandAdmin(ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
