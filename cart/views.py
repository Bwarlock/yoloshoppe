from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .cart import Cart
from order.models import Order
from product.models import Product
from .models import CartModel

def add_to_cart(request, product_id):
    cart = Cart(request)
    cart.add(product_id)
    
    if(request.user.is_authenticated):
        filled = CartModel.objects.filter(user=request.user)
        for item in filled:
            if product_id == item.key:
                break
        else:
            CartModel.objects.create(
                user = request.user,
                key = int(product_id),
                value = int(cart.get_item(product_id)['quantity']),
            )
    return render(request, 'cart/partials/menu_cart.html')

def cart(request):
    return render(request, 'cart/cart.html')

def success(request):
    return render(request, 'cart/success.html')

def failure(request):
    Cart(request).initcart(request)
    orders = Order.objects.filter(user=request.user , paid=False)
    for i in orders:
        i.delete()
    return render(request, 'cart/failure.html')

def update_cart(request, product_id, action):
    cart = Cart(request)

    if action == 'increment':
        cart.add(product_id, 1, True)
        if(request.user.is_authenticated):
            Cartrow = CartModel.objects.get(user=request.user ,key=int(product_id))
            Cartrow.value = Cartrow.value + 1
            Cartrow.save()
    else:
        cart.add(product_id, -1, True)
        if(request.user.is_authenticated):
            Cartrow = CartModel.objects.get(user=request.user ,key=int(product_id))
            Cartrow.value = Cartrow.value - 1
            if (Cartrow.value == 0):
                Cartrow.delete()
            else:
                Cartrow.save()
    
    product = Product.objects.get(pk=product_id)
    quantity = cart.get_item(product_id)
    
    if quantity:
        quantity = quantity['quantity']

        item = {
            'product': {
                'id': product.id,
                'name': product.name,
                'image': product.image,
                'get_thumbnail': product.get_thumbnail(),
                'price': product.price,
                'slug': product.slug,
            },
            'total_price': (quantity * product.price) / 100,
            'quantity': quantity,
        }
    else:
        item = None

    response = render(request, 'cart/partials/cart_item.html', {'item': item})
    response['HX-Trigger'] = 'update-menu-cart'

    return response

@login_required
def checkout(request):
    pub_key = settings.STRIPE_API_KEY_PUBLISHABLE 
    return render(request, 'cart/checkout.html', {'pub_key': pub_key})

def hx_menu_cart(request):
    return render(request, 'cart/partials/menu_cart.html')

def hx_cart_total(request):
    return render(request, 'cart/partials/cart_total.html')