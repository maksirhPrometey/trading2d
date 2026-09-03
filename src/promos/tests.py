from decimal import Decimal

from django.test import Client, TestCase
from django.urls import reverse

from src.cart.models import Cart, CartItem
from src.orders.models import Order
from src.orders.payment import build_payment_data
from src.products.models import Category, Product
from src.promos.models import PromoCode, PromoRedemption
from src.promos.services import create_promo_batch


class PromoCodeTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Cat', description='')
        self.product = Product.objects.create(
            name='P1',
            description='d',
            category=self.category,
            price=Decimal('200.00'),
        )
        self.promo = PromoCode.objects.create(code='SALE10', discount_percent=10)

    def _add_to_cart(self):
        session = self.client.session
        session.save()
        cart = Cart.objects.create(session_key=session.session_key)
        CartItem.objects.create(cart=cart, product=self.product, quantity=1)
        return cart

    def test_apply_updates_payable_total(self):
        self._add_to_cart()
        response = self.client.post(reverse('promo_apply'), {'code': 'sale10', 'next': '/cart/'})
        self.assertEqual(response.status_code, 302)
        cart_page = self.client.get(reverse('cart_detail'))
        self.assertContains(cart_page, 'SALE10')
        self.assertContains(cart_page, '180')

    def test_invalid_code(self):
        self._add_to_cart()
        self.client.post(reverse('promo_apply'), {'code': 'NOPE', 'next': '/cart/'})
        self.assertIsNone(self.client.session.get('applied_promo_code'))

    def test_second_code_replaces_first(self):
        PromoCode.objects.create(code='SALE20', discount_percent=20)
        self._add_to_cart()
        self.client.post(reverse('promo_apply'), {'code': 'SALE10', 'next': '/cart/'})
        self.client.post(reverse('promo_apply'), {'code': 'SALE20', 'next': '/cart/'})
        self.assertEqual(self.client.session.get('applied_promo_code'), 'SALE20')

    def test_min_amount(self):
        self.promo.min_order_amount = Decimal('500.00')
        self.promo.save()
        self._add_to_cart()
        self.client.post(reverse('promo_apply'), {'code': 'SALE10', 'next': '/cart/'})
        self.assertIsNone(self.client.session.get('applied_promo_code'))

    def test_checkout_redeems_and_sets_liqpay_amount(self):
        self._add_to_cart()
        self.client.post(reverse('promo_apply'), {'code': 'SALE10', 'next': '/checkout/'})
        response = self.client.post(
            reverse('checkout'),
            {
                'full_name': 'Guest',
                'phone': '+380501111111',
                'email': '',
                'comment': '',
                'delivery_method': Order.DeliveryMethod.SELF_PICKUP,
                'np_city_name': '',
                'np_city_ref': '',
                'np_warehouse_name': '',
                'np_warehouse_ref': '',
                'payment_method': Order.PaymentMethod.LIQPAY,
            },
        )
        self.assertEqual(response.status_code, 302)
        order = Order.objects.latest('pk')
        self.assertEqual(order.subtotal, Decimal('200.00'))
        self.assertEqual(order.discount_amount, Decimal('20.00'))
        self.assertEqual(order.total, Decimal('180.00'))
        self.assertEqual(order.promo_code, 'SALE10')
        self.assertEqual(order.payable_amount, Decimal('180.00'))
        self.promo.refresh_from_db()
        self.assertEqual(self.promo.used_count, 1)
        self.assertTrue(PromoRedemption.objects.filter(order=order, promo=self.promo).exists())
        self.assertIsNone(self.client.session.get('applied_promo_code'))

    def test_liqpay_uses_total(self):
        order = Order.objects.create(
            full_name='A',
            phone='+38050',
            delivery_method=Order.DeliveryMethod.SELF_PICKUP,
            payment_method=Order.PaymentMethod.LIQPAY,
            subtotal=Decimal('200.00'),
            discount_amount=Decimal('20.00'),
            total=Decimal('180.00'),
        )
        with self.settings(LIQPAY_PUBLIC_KEY='pub', LIQPAY_PRIVATE_KEY='priv', SITE_DOMAIN='x', SITE_PROTOCOL='https'):
            data, _sig = build_payment_data(order)
        import base64
        import json
        payload = json.loads(base64.b64decode(data))
        self.assertEqual(payload['amount'], '180.00')

    def test_generate_batch_separate_rows(self):
        created = create_promo_batch('SUMMER', 3, discount_percent=15)
        self.assertEqual(len(created), 3)
        codes = sorted(p.code for p in created)
        self.assertEqual(codes, ['SUMMER-01', 'SUMMER-02', 'SUMMER-03'])
        self.assertEqual(PromoCode.objects.filter(code__startswith='SUMMER-').count(), 3)
