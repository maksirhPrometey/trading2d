from django.urls import path

from src.wishlist import views

urlpatterns = [
    path('', views.wishlist_detail, name='wishlist_detail'),
    path('toggle/<slug:slug>/', views.wishlist_toggle, name='wishlist_toggle'),
    path('remove/<int:item_id>/', views.wishlist_remove, name='wishlist_remove'),
]
