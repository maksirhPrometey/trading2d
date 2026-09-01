from django.urls import path

from src.orders import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('orders/success/<str:order_number>/', views.order_success, name='order_success'),
    path('orders/nova-poshta/cities/', views.np_cities, name='np_cities'),
    path('orders/nova-poshta/warehouses/', views.np_warehouses, name='np_warehouses'),
    path('orders/liqpay/callback/', views.liqpay_callback, name='liqpay_callback'),
]
