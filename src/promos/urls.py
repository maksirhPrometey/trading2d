from django.urls import path

from src.promos import views

urlpatterns = [
    path('promo/apply/', views.promo_apply, name='promo_apply'),
    path('promo/remove/', views.promo_remove, name='promo_remove'),
]
