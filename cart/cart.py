from django.conf import settings

from product.models import Product
from .models import CartModel

class Cart(object):
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        user = self.session.get(settings.CART_SESSION_USER)
        
        
        if cart is None:
            cart = self.session[settings.CART_SESSION_ID] = {}
            user = self.session[settings.CART_SESSION_USER] = str(request.user)
        

        self.user = user
        if (self.user != str(request.user)):
            if cart != {}:
                try:
                    if (request.user.is_authenticated):
                        filled = CartModel.objects.filter(user=request.user)
                        for item in cart.keys():
                            for i in filled:
                                if int(cart[item]['id']) == i.key:
                                    break
                            else:
                                CartModel.objects.create(
                                    user = request.user,
                                    key = int(cart[item]['id']),
                                    value = int(cart[item]['quantity']),
                                )
                except Exception as err:
                    print(err.with_traceback())

            self.user = self.session[settings.CART_SESSION_USER] = str(request.user)
            cart = self.session[settings.CART_SESSION_ID] = {}
            try:
                if (request.user.is_authenticated):
                    filled = CartModel.objects.filter(user=request.user)
                    if filled:
                        for item in filled:
                            cart[str(item.key)] = {'quantity': item.value, 'id': str(item.key)}
            except Exception as err:
                print(err.with_traceback())
        self.cart = cart
        

    def __iter__(self):
        for p in self.cart.keys():
            self.cart[str(p)]['product'] = Product.objects.get(pk=p)
        
        for item in self.cart.values():
            item['total_price'] = int(item['product'].price * item['quantity']) / 100

            yield item
    
    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())
    
    def initcart(self , request):
        cart = {}
        try:
            if (request.user.is_authenticated):
                filled = CartModel.objects.filter(user=request.user)
                if filled:
                    for item in filled:
                        cart[str(item.key)] = {'quantity': item.value, 'id': str(item.key)}
        except Exception as err:
            print(err.with_traceback())
        self.cart = cart
        self.save()
    
    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True
    
    def add(self, product_id, quantity=1, update_quantity=False):
        product_id = str(product_id)

        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': quantity, 'id': product_id}
        
        if update_quantity:
            self.cart[product_id]['quantity'] += int(quantity)

            if self.cart[product_id]['quantity'] == 0:
                self.remove(product_id)
        
        
        self.save()
    
    def remove(self, product_id):
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
    
    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True
    
    def get_total_cost(self):
        for p in self.cart.keys():
            self.cart[str(p)]['product'] = Product.objects.get(pk=p)

        return int(sum(item['product'].price * item['quantity'] for item in self.cart.values())) / 100
    
    def get_item(self, product_id):
        if str(product_id) in self.cart:
            return self.cart[str(product_id)]
        else:
            return None