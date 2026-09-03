from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import FormView

from src.accounts.forms import LoginForm, ProfileForm, RegistrationForm
from src.accounts.models import Profile
from src.accounts.services import merge_guest_cart, merge_guest_wishlist
from src.orders.models import Order


class AccountLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        # login() ротує session_key — зливаємо гостьові дані ДО ротації
        session_key = self.request.session.session_key
        user = form.get_user()
        merge_guest_cart(user, session_key)
        merge_guest_wishlist(user, session_key)
        return super().form_valid(form)


class AccountLogoutView(LogoutView):
    next_page = reverse_lazy('home')
    http_method_names = ['post', 'options']


class AccountRegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('accounts:profile')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('accounts:profile')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        session_key = self.request.session.session_key
        user = form.save()
        merge_guest_cart(user, session_key)
        merge_guest_wishlist(user, session_key)
        login(self.request, user)
        messages.success(self.request, _('Акаунт створено. Ласкаво просимо!'))
        return super().form_valid(form)


class AccountPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in form.fields.values():
            field.widget.attrs['class'] = 'auth-field__input'
            field.widget.attrs.setdefault('autocomplete', 'email')
        return form


class AccountPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in form.fields.values():
            field.widget.attrs['class'] = 'auth-field__input'
            field.widget.attrs.setdefault('autocomplete', 'new-password')
        return form


class AccountPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class AccountPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'


@login_required
def profile(request):
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile_obj, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Профіль оновлено.'))
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=profile_obj, user=request.user)

    orders_qs = request.user.orders.exclude(status=Order.Status.CANCELLED)
    stats = orders_qs.aggregate(count=Count('id'), total=Sum('total'))
    recent_orders = (
        request.user.orders.select_related()
        .prefetch_related('items')
        .order_by('-created_at')[:10]
    )

    return render(
        request,
        'accounts/profile.html',
        {
            'form': form,
            'profile': profile_obj,
            'stats': stats,
            'recent_orders': recent_orders,
            'account_nav': 'profile',
        },
    )


@login_required
def order_list(request):
    orders = (
        request.user.orders.prefetch_related('items')
        .order_by('-created_at')
    )
    return render(
        request,
        'accounts/order_list.html',
        {
            'orders': orders,
            'account_nav': 'orders',
        },
    )


@login_required
def order_detail(request, order_number):
    order = get_object_or_404(
        Order.objects.prefetch_related('items'),
        order_number=order_number,
        user=request.user,
    )
    return render(
        request,
        'accounts/order_detail.html',
        {
            'order': order,
            'account_nav': 'orders',
        },
    )
