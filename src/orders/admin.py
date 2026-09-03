from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import ChoicesDropdownFilter, RangeDateFilter
from unfold.decorators import display

from src.orders.models import Order, OrderItem


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    tab = True
    readonly_fields = (
        'product',
        'product_name',
        'product_sku',
        'unit_price',
        'quantity',
        'line_total_display',
    )
    fields = readonly_fields

    @display(description='Сума')
    def line_total_display(self, obj):
        if obj.pk:
            return obj.line_total
        return '—'


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = (
        'order_number',
        'user',
        'full_name',
        'phone',
        'status_badge',
        'subtotal',
        'paid_badge',
        'created_at',
    )
    list_filter = (
        ('status', ChoicesDropdownFilter),
        ('delivery_method', ChoicesDropdownFilter),
        ('payment_method', ChoicesDropdownFilter),
        'is_paid',
        ('created_at', RangeDateFilter),
    )
    search_fields = ('order_number', 'full_name', 'phone', 'email', 'user__username')
    readonly_fields = (
        'order_number',
        'subtotal',
        'session_key',
        'payment_transaction_id',
        'created_at',
        'updated_at',
    )
    raw_id_fields = ('user',)
    inlines = (OrderItemInline,)
    warn_unsaved_form = True
    list_per_page = 25
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Замовлення', {'fields': ('order_number', 'status', 'user', 'created_at', 'updated_at')}),
        ('Покупець', {'fields': ('full_name', 'phone', 'email', 'comment')}),
        (
            'Доставка',
            {
                'fields': (
                    'delivery_method',
                    'np_city_name',
                    'np_city_ref',
                    'np_warehouse_name',
                    'np_warehouse_ref',
                ),
            },
        ),
        (
            'Оплата',
            {'fields': ('payment_method', 'is_paid', 'subtotal', 'payment_transaction_id')},
        ),
        ('Службове', {'classes': ('collapse',), 'fields': ('session_key',)}),
    )

    @display(
        description='Статус',
        label={
            Order.Status.NEW: 'info',
            Order.Status.CONFIRMED: 'info',
            Order.Status.PAID: 'success',
            Order.Status.SHIPPED: 'warning',
            Order.Status.DONE: 'success',
            Order.Status.CANCELLED: 'danger',
        },
    )
    def status_badge(self, obj):
        return obj.status

    @display(description='Оплата', boolean=True)
    def paid_badge(self, obj):
        return obj.is_paid
