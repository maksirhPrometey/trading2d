from django.urls import path

from src.accounts import views

app_name = 'accounts'

urlpatterns = [
    path('accounts/login/', views.AccountLoginView.as_view(), name='login'),
    path('accounts/logout/', views.AccountLogoutView.as_view(), name='logout'),
    path('accounts/register/', views.AccountRegisterView.as_view(), name='register'),
    path(
        'accounts/password-reset/',
        views.AccountPasswordResetView.as_view(),
        name='password_reset',
    ),
    path(
        'accounts/password-reset/done/',
        views.AccountPasswordResetDoneView.as_view(),
        name='password_reset_done',
    ),
    path(
        'accounts/password-reset/<uidb64>/<token>/',
        views.AccountPasswordResetConfirmView.as_view(),
        name='password_reset_confirm',
    ),
    path(
        'accounts/password-reset/complete/',
        views.AccountPasswordResetCompleteView.as_view(),
        name='password_reset_complete',
    ),
    path('account/', views.profile, name='profile'),
    path('account/orders/', views.order_list, name='order_list'),
    path(
        'account/orders/<str:order_number>/',
        views.order_detail,
        name='order_detail',
    ),
]
