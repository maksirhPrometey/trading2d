from tinymce.widgets import AdminTinyMCE

from src.website.html_sanitize import sanitize_html


class TinyMCEAdminMixin:
    tinymce_fields = ()

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in self.tinymce_fields:
            kwargs['widget'] = AdminTinyMCE()
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        for field_name in self.tinymce_fields:
            value = getattr(obj, field_name, None)
            if value:
                setattr(obj, field_name, sanitize_html(value))
        super().save_model(request, obj, form, change)
