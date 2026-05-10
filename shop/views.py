from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login
from django.contrib.auth.views import LoginView  # Додаємо це
from .models import Product


# Створюємо власний клас для входу
class MyLoginView(LoginView):
    template_name = 'login.html'


def index(request):
    cat_filter = request.GET.get('category')
    sort = request.GET.get('sort')
    products = Product.objects.all()

    if cat_filter:
        products = products.filter(category=cat_filter)

    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-id')
    elif sort == 'oldest':
        products = products.order_by('id')

    return render(request, "index.html", {
        "products": products,
        "categories": Product.CATEGORY_CHOICES,
        "current_category": cat_filter,
        "current_sort": sort
    })


@login_required
def add_product(request):
    if request.method == "POST":
        Product.objects.create(
            name=request.POST["name"],
            category=request.POST["category"],
            price=request.POST["price"],
            image=request.FILES.get("image")
        )
        return redirect("/")
    return render(request, "add.html", {"categories": Product.CATEGORY_CHOICES})


@login_required
def delete_product(request, product_id):
    Product.objects.get(id=product_id).delete()
    return redirect("/")


def logout_user(request):
    logout(request)
    return redirect("/")


def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart
    return redirect("/")


def cart_detail(request):
    cart = request.session.get('cart', {})
    products_in_cart = []
    total_price = 0
    for p_id, qty in cart.items():
        try:
            p = Product.objects.get(id=p_id)
            item_total = p.price * qty
            total_price += item_total
            products_in_cart.append({'product': p, 'quantity': qty, 'item_total': item_total})
        except Product.DoesNotExist:
            continue
    return render(request, "cart.html", {'cart_items': products_in_cart, 'total_price': total_price})


def clear_cart(request):
    if 'cart' in request.session: del request.session['cart']
    return redirect("/cart/")