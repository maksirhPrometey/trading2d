from django.contrib import admin
from unfold.admin import ModelAdmin

from src.accounts.models import Profile


@admin.register(Profile)
class ProfileAdmin(ModelAdmin):
    list_display = ('user', 'phone', 'updated_at')
    search_fields = ('user__username', 'user__email', 'phone')
    raw_id_fields = ('user',)
