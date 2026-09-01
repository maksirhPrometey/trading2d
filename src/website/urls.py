from django.urls import path
from src.website.views import (
    home,
    contact,
    about_us,
    delivery_and_payment,
    privacy_policy,
    terms_and_conditions,
)


urlpatterns = [
    path('', home, name='home'),
    path('contact/', contact, name='contact'),
    path('about-us/', about_us, name='about_us'),
    path('delivery/', delivery_and_payment, name='delivery'),
    path('privacy-policy/', privacy_policy, name='privacy_policy'),
    path('terms-and-conditions/', terms_and_conditions, name='terms_and_conditions'),
]

