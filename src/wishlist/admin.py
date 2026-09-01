from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from src.wishlist.models import Wishlist, WishlistItem


class WishlistItemInline(TabularInline):
    model = WishlistItem
    extra = 0
    tab = True
    readonly_fields = ('created_at',)


@admin.register(Wishlist)
class WishlistAdmin(ModelAdmin):
    list_display = ('id', 'user', 'session_key', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('session_key', 'user__username', 'user__email')
    inlines = (WishlistItemInline,)
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('user',)
