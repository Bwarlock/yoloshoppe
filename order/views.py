import json
import time
import stripe

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from cart.cart import Cart
from product.models import Product
from .models import Order, OrderItem
from cart.models import CartModel

def start_order(request):
    cart = Cart(request)
    data = json.loads(request.body)
    total_price = 0

    items = []

    for item in cart:
        product = item['product']
        total_price += product.price * int(item['quantity'])

        items.append({
            'price_data': {
                'currency': 'inr',
                'product_data': {
                    'name': product.name,
                },
                'unit_amount': product.price,
            },
            'quantity': item['quantity']
        })
    
    order = Order.objects.create(
        user=request.user, 
        first_name=data['first_name'], 
        last_name=data['last_name'], 
        email=data['email'], 
        phone=data['phone'], 
        address=data['address'], 
        zipcode=data['zipcode'], 
        place=data['place'],
        paid=False,
        paid_amount=total_price
    )

    stripe.api_key = settings.STRIPE_API_KEY_HIDDEN
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=items,
        metadata = {'orderid' : order.id , 'user' : request.user.id},
        mode='payment',
        success_url=f'{settings.WEBSITE_URL}cart/success/',
        cancel_url=f'{settings.WEBSITE_URL}cart/failure/',
    )
    payment_intent = session.payment_intent
    print('pay' , payment_intent)
    cart.clear()

    return JsonResponse({'session': session, 'order': payment_intent})



@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    time.sleep(2)
    try:
        event = stripe.Webhook.construct_event(
        payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        print(event['type'])
        print('first reach')
    except ValueError as e:
        print('1st err' , e)
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print('2nd err' , e)
        return HttpResponse(status=400)
    
    if event['type'] == 'checkout.session.completed':
        print('reached')
        session = event['data']['object']
        print(session["metadata"])
        order = Order.objects.get(pk=int(session['metadata']['orderid']))
        order.paid = True
        order.save()

        cartItems = CartModel.objects.filter(user=int(session['metadata']['user']))
        for Citem in cartItems:
            print(Citem)
            product = Product.objects.get(pk=Citem.key)
            quantity = Citem.value
            price = product.price * quantity

            item = OrderItem.objects.create(order=order, product=product, price=price, quantity=quantity)
            Citem.delete()
        

    return HttpResponse(status=200)