from django.urls import path

from src.cart import views

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<slug:slug>/', views.cart_add, name='cart_add'),
    path('update/<int:item_id>/', views.cart_update, name='cart_update'),
    path('remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
]
