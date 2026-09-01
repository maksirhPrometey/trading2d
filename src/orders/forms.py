from django import forms
from django.utils.translation import gettext_lazy as _

from src.orders.models import Order


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'full_name', 'phone', 'email', 'comment',
            'delivery_method', 'np_city_name', 'np_city_ref',
            'np_warehouse_name', 'np_warehouse_ref', 'payment_method',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-input', 'autocomplete': 'name'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'autocomplete': 'tel', 'placeholder': '+380'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'autocomplete': 'email'}),
            'comment': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'np_city_name': forms.TextInput(attrs={'class': 'form-input', 'id': 'np-city-input', 'autocomplete': 'off'}),
            'np_city_ref': forms.HiddenInput(),
            'np_warehouse_name': forms.TextInput(attrs={'class': 'form-input', 'id': 'np-warehouse-input', 'autocomplete': 'off'}),
            'np_warehouse_ref': forms.HiddenInput(),
            'delivery_method': forms.RadioSelect(attrs={'class': 'catalog-checkbox'}),
            'payment_method': forms.RadioSelect(attrs={'class': 'catalog-checkbox'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ModelForm автоматично додає порожній вибір "---------" для CharField
        # без default, навіть якщо поле обов'язкове (blank=False) — для
        # RadioSelect це виглядає як зайва нерелевантна опція. Прибираємо її
        # та одразу підставляємо перший варіант, щоб форма не була порожньою.
        self.fields['delivery_method'].choices = Order.DeliveryMethod.choices
        self.fields['payment_method'].choices = Order.PaymentMethod.choices
        if not self.initial.get('delivery_method'):
            self.initial['delivery_method'] = Order.DeliveryMethod.choices[0][0]
        if not self.initial.get('payment_method'):
            self.initial['payment_method'] = Order.PaymentMethod.choices[0][0]

    def clean(self):
        cleaned = super().clean()
        delivery_method = cleaned.get('delivery_method')
        if delivery_method == Order.DeliveryMethod.NOVA_POSHTA_WAREHOUSE:
            if not cleaned.get('np_city_ref') or not cleaned.get('np_warehouse_ref'):
                raise forms.ValidationError(_('Оберіть місто та відділення Нової Пошти зі списку.'))
        return cleaned
