from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from src.cart.models import Cart, CartItem


class CartItemInline(TabularInline):
    model = CartItem
    extra = 0
    tab = True
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Cart)
class CartAdmin(ModelAdmin):
    list_display = ('id', 'user', 'session_key', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('session_key', 'user__username', 'user__email')
    inlines = (CartItemInline,)
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('user',)
