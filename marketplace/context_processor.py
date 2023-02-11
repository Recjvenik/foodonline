from .models import Cart
from menu.models import FoodItem
from django.db.models import Sum


def get_cart_count(request):
    cart_count = 0
    if request.user.is_authenticated:
        # cart_count = Cart.objects.filter(user=request.user).aaggregate(Sum('quantity'))
        try:
            cart_items = Cart.objects.filter(user=request.user)
            if cart_items.exists():
                for cart_item in cart_items:
                    cart_count += cart_item.quantity
        except:
            cart_count = 0
    return dict(cart_count=cart_count)        


def get_cart_ammounts(request):
    subtotal = 0
    tax = 0
    grand_total = 0
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            food_item = FoodItem.objects.get(pk=item.fooditem.id)
            subtotal += (food_item.price * item.quantity)
        
        grand_total = subtotal + tax
    return dict(subtotal=subtotal, tax=tax, grand_total=grand_total)