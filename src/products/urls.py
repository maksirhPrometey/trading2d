from django.urls import path

from src.products import views

urlpatterns = [
    path('catalog/', views.catalog_list, name='catalog'),
    path('catalog/<slug:slug>/', views.product_detail, name='product_detail'),
]
