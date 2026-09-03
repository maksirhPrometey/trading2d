from django import forms
from django.utils.translation import gettext_lazy as _

from src.promos.models import PromoCode
from src.promos.services import normalize_code


class ApplyPromoForm(forms.Form):
    code = forms.CharField(
        max_length=32,
        label=_('Промокод'),
        widget=forms.TextInput(attrs={
            'class': 'promo-form__input',
            'autocomplete': 'off',
            'autocapitalize': 'characters',
            'spellcheck': 'false',
            'inputmode': 'text',
        }),
    )

    def clean_code(self):
        return normalize_code(self.cleaned_data['code'])


class PromoCodeAdminForm(forms.ModelForm):
    generate_count = forms.IntegerField(
        min_value=1,
        max_value=200,
        initial=1,
        required=False,
        label=_('Кількість кодів'),
        help_text=_('1 — зберегти цей код. Більше 1 — окремі рядки: КОД-01, КОД-02…'),
    )

    class Meta:
        model = PromoCode
        fields = (
            'code',
            'discount_percent',
            'is_active',
            'valid_from',
            'valid_until',
            'min_order_amount',
            'max_uses',
            'max_uses_per_customer',
            'note',
        )

    def clean_code(self):
        return normalize_code(self.cleaned_data['code'])

    def clean_generate_count(self):
        return self.cleaned_data.get('generate_count') or 1
