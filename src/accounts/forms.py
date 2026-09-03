from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from src.accounts.models import Profile

User = get_user_model()

AUTH_INPUT_CLASS = 'auth-field__input'


def _apply_auth_widgets(form, autocomplete_map=None):
    autocomplete_map = autocomplete_map or {}
    for name, field in form.fields.items():
        field.widget.attrs['class'] = AUTH_INPUT_CLASS
        if name in autocomplete_map:
            field.widget.attrs.setdefault('autocomplete', autocomplete_map[name])


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = _('Email або логін')
        self.fields['username'].help_text = ''
        self.fields['password'].help_text = ''
        _apply_auth_widgets(
            self,
            {
                'username': 'username',
                'password': 'current-password',
            },
        )


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(label=_('Email'), required=True)
    first_name = forms.CharField(label=_("Ім'я"), max_length=150, required=False)
    phone = forms.CharField(label=_('Телефон'), max_length=32, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'phone', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = _(
            'До 150 символів. Літери, цифри та @/./+/-/_.'
        )
        self.fields['password1'].help_text = _(
            'Мінімум 8 символів. Без поширених паролів.'
        )
        self.fields['password2'].help_text = _(
            'Повторіть пароль для підтвердження.'
        )
        self.fields['email'].help_text = ''
        self.fields['first_name'].help_text = ''
        self.fields['phone'].help_text = ''
        _apply_auth_widgets(
            self,
            {
                'username': 'username',
                'email': 'email',
                'first_name': 'given-name',
                'phone': 'tel',
                'password1': 'new-password',
                'password2': 'new-password',
            },
        )
        self.fields['phone'].widget.attrs.setdefault('inputmode', 'tel')

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_('Користувач з таким email уже існує.'))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        if commit:
            user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            phone = self.cleaned_data.get('phone', '').strip()
            if phone:
                profile.phone = phone
                profile.save(update_fields=['phone', 'updated_at'])
        return user


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(label=_("Ім'я"), max_length=150, required=False)
    last_name = forms.CharField(label=_('Прізвище'), max_length=150, required=False)
    email = forms.EmailField(label=_('Email'), required=True)

    class Meta:
        model = Profile
        fields = ('phone',)
        widgets = {
            'phone': forms.TextInput(
                attrs={
                    'class': 'form-input',
                    'autocomplete': 'tel',
                    'inputmode': 'tel',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['first_name'].initial = self.user.first_name
        self.fields['last_name'].initial = self.user.last_name
        self.fields['email'].initial = self.user.email
        for name in ('first_name', 'last_name', 'email'):
            self.fields[name].widget.attrs['class'] = 'form-input'
        self.fields['first_name'].widget.attrs['autocomplete'] = 'given-name'
        self.fields['last_name'].widget.attrs['autocomplete'] = 'family-name'
        self.fields['email'].widget.attrs['autocomplete'] = 'email'

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        qs = User.objects.filter(email__iexact=email).exclude(pk=self.user.pk)
        if qs.exists():
            raise forms.ValidationError(_('Користувач з таким email уже існує.'))
        return email

    def save(self, commit=True):
        profile = super().save(commit=False)
        self.user.first_name = self.cleaned_data.get('first_name', '')
        self.user.last_name = self.cleaned_data.get('last_name', '')
        self.user.email = self.cleaned_data['email']
        if commit:
            self.user.save(update_fields=['first_name', 'last_name', 'email'])
            profile.save()
        return profile
