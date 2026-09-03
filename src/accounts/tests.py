from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from src.accounts.models import Profile
from src.accounts.services import merge_guest_cart, merge_guest_wishlist
from src.cart.models import Cart, CartItem
from src.orders.models import Order
from src.products.models import Category, Product
from src.wishlist.models import Wishlist, WishlistItem

User = get_user_model()


class AccountsAuthTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_creates_user_and_profile(self):
        response = self.client.post(
            reverse('accounts:register'),
            {
                'username': 'buyer1',
                'email': 'Buyer1@Example.com',
                'first_name': 'Олег',
                'phone': '+380501112233',
                'password1': 'Str0ngPass!99',
                'password2': 'Str0ngPass!99',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('accounts:profile'))
        user = User.objects.get(username='buyer1')
        self.assertEqual(user.email, 'buyer1@example.com')
        self.assertTrue(Profile.objects.filter(user=user, phone='+380501112233').exists())
        self.assertTrue(self.client.session.get('_auth_user_id'))

    def test_login_and_profile_requires_auth(self):
        anon = self.client.get(reverse('accounts:profile'))
        self.assertEqual(anon.status_code, 302)
        self.assertIn('/accounts/login/', anon['Location'])

        User.objects.create_user('buyer2', 'b2@ex.com', 'Str0ngPass!99')
        ok = self.client.post(
            reverse('accounts:login'),
            {'username': 'buyer2', 'password': 'Str0ngPass!99'},
        )
        self.assertEqual(ok.status_code, 302)
        profile = self.client.get(reverse('accounts:profile'))
        self.assertEqual(profile.status_code, 200)
        self.assertContains(profile, 'data-qa="account-link"')

    def test_header_shows_login_for_anonymous(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'data-qa="login-link"')
        self.assertNotContains(response, 'data-qa="account-link"')


class AccountsMergeTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Cat', description='')
        self.product = Product.objects.create(
            name='P1',
            description='d',
            category=self.category,
            price=Decimal('100.00'),
        )
        self.user = User.objects.create_user('merger', 'm@ex.com', 'Str0ngPass!99')

    def test_merge_guest_cart_sums_qty(self):
        session = self.client.session
        session.save()
        guest = Cart.objects.create(session_key=session.session_key, user=None)
        CartItem.objects.create(cart=guest, product=self.product, quantity=2)
        user_cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=user_cart, product=self.product, quantity=1)

        merge_guest_cart(self.user, session.session_key)
        user_cart.refresh_from_db()
        item = user_cart.items.get(product=self.product)
        self.assertEqual(item.quantity, 3)
        self.assertFalse(Cart.objects.filter(pk=guest.pk).exists())

    def test_merge_on_login(self):
        session = self.client.session
        session.save()
        guest_w = Wishlist.objects.create(session_key=session.session_key, user=None)
        WishlistItem.objects.create(wishlist=guest_w, product=self.product)

        self.client.post(
            reverse('accounts:login'),
            {'username': 'merger', 'password': 'Str0ngPass!99'},
        )
        user_list = Wishlist.objects.get(user=self.user)
        self.assertTrue(user_list.items.filter(product=self.product).exists())
        self.assertFalse(Wishlist.objects.filter(pk=guest_w.pk).exists())


class AccountsOrderScopeTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Cat', description='')
        self.product = Product.objects.create(
            name='P2',
            description='d',
            category=self.category,
            price=Decimal('50.00'),
        )
        self.owner = User.objects.create_user('owner', 'o@ex.com', 'Str0ngPass!99')
        self.other = User.objects.create_user('other', 'x@ex.com', 'Str0ngPass!99')
        self.order = Order.objects.create(
            user=self.owner,
            full_name='Owner',
            phone='+380501111111',
            delivery_method=Order.DeliveryMethod.SELF_PICKUP,
            payment_method=Order.PaymentMethod.COD,
            subtotal=Decimal('50.00'),
        )

    def test_order_list_hides_foreign_orders(self):
        self.client.force_login(self.other)
        response = self.client.get(reverse('accounts:order_list'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.order.order_number)

    def test_order_detail_idor(self):
        self.client.force_login(self.other)
        response = self.client.get(
            reverse('accounts:order_detail', args=[self.order.order_number]),
        )
        self.assertEqual(response.status_code, 404)

        self.client.force_login(self.owner)
        ok = self.client.get(
            reverse('accounts:order_detail', args=[self.order.order_number]),
        )
        self.assertEqual(ok.status_code, 200)
        self.assertContains(ok, self.order.order_number)

    def test_checkout_sets_user_when_authenticated(self):
        self.client.force_login(self.owner)
        cart = Cart.objects.create(user=self.owner)
        CartItem.objects.create(cart=cart, product=self.product, quantity=1)
        response = self.client.post(
            reverse('checkout'),
            {
                'full_name': 'Owner Name',
                'phone': '+380501111111',
                'email': 'o@ex.com',
                'comment': '',
                'delivery_method': Order.DeliveryMethod.SELF_PICKUP,
                'np_city_name': '',
                'np_city_ref': '',
                'np_warehouse_name': '',
                'np_warehouse_ref': '',
                'payment_method': Order.PaymentMethod.COD,
            },
        )
        self.assertEqual(response.status_code, 302)
        order = Order.objects.exclude(pk=self.order.pk).latest('pk')
        self.assertEqual(order.user_id, self.owner.id)
        self.assertEqual(
            self.client.session.get('last_order_number'),
            order.order_number,
        )

    def test_guest_success_requires_session(self):
        guest_order = Order.objects.create(
            full_name='Guest',
            phone='+380502222222',
            delivery_method=Order.DeliveryMethod.SELF_PICKUP,
            payment_method=Order.PaymentMethod.COD,
            subtotal=Decimal('10.00'),
        )
        blocked = self.client.get(
            reverse('order_success', args=[guest_order.order_number]),
        )
        self.assertEqual(blocked.status_code, 404)

        session = self.client.session
        session['last_order_id'] = guest_order.pk
        session['last_order_number'] = guest_order.order_number
        session.save()
        ok = self.client.get(
            reverse('order_success', args=[guest_order.order_number]),
        )
        self.assertEqual(ok.status_code, 200)
