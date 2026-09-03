from django.contrib import admin, messages
from unfold.admin import ModelAdmin

from src.promos.forms import PromoCodeAdminForm
from src.promos.models import PromoCode, PromoRedemption
from src.promos.services import create_promo_batch


@admin.register(PromoCode)
class PromoCodeAdmin(ModelAdmin):
    form = PromoCodeAdminForm
    list_display = (
        'code',
        'discount_percent',
        'is_active',
        'valid_until',
        'used_count',
        'max_uses',
        'min_order_amount',
    )
    list_filter = ('is_active',)
    search_fields = ('code', 'note')
    readonly_fields = ('used_count', 'created_at', 'updated_at')
    list_per_page = 25
    fieldsets = (
        ('Код', {'fields': ('code', 'generate_count', 'discount_percent', 'is_active', 'note')}),
        ('Термін і сума', {'fields': ('valid_from', 'valid_until', 'min_order_amount')}),
        ('Ліміти', {'fields': ('max_uses', 'max_uses_per_customer', 'used_count')}),
        ('Службове', {'classes': ('collapse',), 'fields': ('created_at', 'updated_at')}),
    )

    def get_fieldsets(self, request, obj=None):
        if obj:
            return (
                ('Код', {'fields': ('code', 'discount_percent', 'is_active', 'note')}),
                ('Термін і сума', {'fields': ('valid_from', 'valid_until', 'min_order_amount')}),
                ('Ліміти', {'fields': ('max_uses', 'max_uses_per_customer', 'used_count')}),
                ('Службове', {'classes': ('collapse',), 'fields': ('created_at', 'updated_at')}),
            )
        return super().get_fieldsets(request, obj)

    def save_model(self, request, obj, form, change):
        count = form.cleaned_data.get('generate_count') or 1
        if change or count == 1:
            super().save_model(request, obj, form, change)
            return
        fields = {
            'discount_percent': obj.discount_percent,
            'is_active': obj.is_active,
            'valid_from': obj.valid_from,
            'valid_until': obj.valid_until,
            'min_order_amount': obj.min_order_amount,
            'max_uses': obj.max_uses,
            'max_uses_per_customer': obj.max_uses_per_customer,
            'note': obj.note,
        }
        created = create_promo_batch(obj.code, count, **fields)
        obj.pk = created[0].pk
        obj.code = created[0].code
        self._batch_count = len(created)
        messages.success(request, f'Створено {len(created)} окремих промокодів.')

    def response_add(self, request, obj, post_url_continue=None):
        if getattr(self, '_batch_count', 0) > 1:
            return self.response_post_save_add(request, obj)
        return super().response_add(request, obj, post_url_continue)


@admin.register(PromoRedemption)
class PromoRedemptionAdmin(ModelAdmin):
    list_display = ('promo', 'order', 'user', 'phone', 'created_at')
    search_fields = ('promo__code', 'order__order_number', 'phone', 'user__username')
    raw_id_fields = ('promo', 'order', 'user')
    readonly_fields = ('promo', 'order', 'user', 'session_key', 'phone', 'created_at')

    def has_add_permission(self, request):
        return False
