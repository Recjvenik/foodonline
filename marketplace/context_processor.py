from .models import Cart, Tax
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
    tax_dict = {}
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            food_item = FoodItem.objects.get(pk=item.fooditem.id)
            subtotal += (food_item.price * item.quantity)
        
        get_tax = Tax.objects.filter(is_active=True)
        for i_tax in get_tax:
            tax_type = i_tax.tax_type
            tax_percentage = i_tax.tax_percentage 
            tax_amount = round((subtotal * tax_percentage)/100, 2)
            tax_dict.update({tax_type: {str(tax_percentage): tax_amount}})

        tax = sum(x for key in tax_dict.values() for x in key.values())
    
    grand_total = subtotal + tax
    return dict(subtotal=subtotal, tax=tax, grand_total=grand_total, tax_dict=tax_dict)