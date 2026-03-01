from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Product, Review, CartItem
from .forms import OrderForm, ReviewForm
from .models import Order, OrderItem
import random
import logging
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


def home(request):
    featured_products = Product.objects.filter(is_available=True)[:4]
    latest_reviews = Review.objects.all().order_by('-created_at')[:3]
    return render(request, 'confectionery/home.html', {
        'title': 'Главная страница',
        'welcome_message': 'Добро пожаловать!',
        'featured_products': featured_products,
        'reviews': latest_reviews
    })


class ProductListView(ListView):
    """Класс для отображения списка товаров на странице"""

    model = Product
    template_name = 'confectionery/products.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        return Product.objects.filter(is_available=True).order_by('created_at')


def about(request):
    return render(request, 'confectionery/about.html', {
        'title': 'О нашей кондитерской',
    })


@login_required
def cart_view(request):
    return render(request, 'confectionery/cart.html', {
        'cart_items': request.cart["items"],
        'total': request.cart["total_price"],
        'cart_items_count': request.cart["total_qty"]
    })


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(
        product=product,
        user=request.user,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f'{product.name} добавлен в корзину.')
    return redirect('product_list')


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    return redirect('cart')


@login_required
def reviews(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.author = request.user.username
            review.save()

            try:
                send_mail(
                    subject='Новый отзыв на сайте',
                    message=(
                        f'Пользователь: {request.user.username}\n'
                        f'Оценка: {review.rating}\n\n'
                        f'Текст отзыва:\n{review.text}'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.EMAIL_HOST_USER],
                    fail_silently=False,
                )
            except Exception as e:
                print(f'Ошибка отправки письма: {e}')

            messages.success(request, 'Ваш отзыв отправлен.')
            return redirect('reviews')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')

    else:
        form = ReviewForm()

    reviews_list = Review.objects.all().order_by('-created_at')

    return render(request, 'confectionery/reviews.html', {
        'form': form,
        'reviews': reviews_list,
        'title': 'Отзывы наших клиентов'
    })


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'confectionery/register.html', {'form': form})


@login_required
def order_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.product.price * item.quantity for item in cart_items)

    if not cart_items:
        return redirect('cart')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.order_number = f"{random.randint(100000, 999999)}"
            order.save()

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
            cart_items.delete()
            return redirect('order_success', order_id=order.id)
    else:
        form = OrderForm()

    return render(request, 'confectionery/order.html', {
        'form': form,
        'cart_items': cart_items,
        'total': total
    })


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'confectionery/order_success.html', {'order': order})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'confectionery/order_detail.html', {'order': order})


@login_required
def order_history(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .prefetch_related('items')
        .order_by('-created_at')
    )

    return render(request, 'confectionery/order_history.html', {
        'orders': orders,
        'title': 'Мои заказы'
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'confectionery/product_detail.html', {'product': product})


def custom_404_view(request, exception):
    return render(request, 'confectionery/404.html', status=404)
