from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from django.http import HttpResponse
from myapp.middleware import CartMiddleware
from myapp.models import CartItem, Product


class CartMiddlewareTests(TestCase):
    """
    Тесты для анонимного пользователя, авторизованного пользователя
    с корзиной и без.
    """

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser",
            password="12345"
        )

        self.product = Product.objects.create(
            name="Торт",
            price=100
        )

    def get_response(self, request):
        return HttpResponse("OK")

    def test_anonymous_user_cart(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()

        middleware = CartMiddleware(self.get_response)
        middleware(request)

        self.assertEqual(request.cart["total_qty"], 0)
        self.assertEqual(request.cart["total_price"], 0)
        self.assertFalse(request.cart["has_items"])
        self.assertEqual(request.cart["items"], [])

    def test_authenticated_user_empty_cart(self):
        request = self.factory.get("/")
        request.user = self.user

        middleware = CartMiddleware(self.get_response)
        middleware(request)

        self.assertEqual(request.cart["total_qty"], 0)
        self.assertEqual(request.cart["total_price"], 0)
        self.assertFalse(request.cart["has_items"])

    def test_authenticated_user_with_items(self):
        CartItem.objects.create(
            user=self.user,
            product=self.product,
            quantity=2
        )

        request = self.factory.get("/")
        request.user = self.user

        middleware = CartMiddleware(self.get_response)
        middleware(request)

        self.assertEqual(request.cart["total_qty"], 2)
        self.assertEqual(request.cart["total_price"], 200)
        self.assertTrue(request.cart["has_items"])
        self.assertEqual(len(request.cart["items"]), 1)
