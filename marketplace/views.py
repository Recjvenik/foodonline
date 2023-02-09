from django.shortcuts import get_object_or_404, render
from vendor.models import Vendor
from menu.models import Category, FoodItem
from .models import Cart
from .context_processor import get_cart_count, get_cart_ammounts
from django.db.models import Prefetch
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required 
# Create your views here.

def market_place(request):
    context = {}
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vemdor_count = vendors.count()
    context['vemdor_count'] = vemdor_count
    context['vendors'] = vendors

    return render(request, 'marketplace/market_listings.html', context)


def vendor_detail(request, vendor_slug=None):
    context = {}
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset = FoodItem.objects.filter(is_available=True)
        )
    )
    
    cart_item= None
    if request.user.is_authenticated:
        cart_item = Cart.objects.filter(user=request.user)
    
        context['cart_item'] = cart_item
    context['vendor'] = vendor
    context['categories'] = categories
    return render(request, 'marketplace/vendor_detail.html', context)


def add_to_cart(request):
    
    if request.user.is_authenticated:
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest': 
            food_id = request.GET.get('food_id')
            try:
                fooditem = FoodItem.objects.get(id=int(food_id))
                try:
                    check_cart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    check_cart.quantity += 1
                    check_cart.save()
                    return JsonResponse({'status': 'Success', 'message': 'Incresed the cart quantity', 'cart_counter': get_cart_count(request), 'qty': check_cart.quantity, 'cart_amount': get_cart_ammounts(request)})
                except:
                    check_cart = Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)
                    return JsonResponse({'status': 'Success', 'message': 'Added the food to the cart', 'cart_counter': get_cart_count(request), 'qty': check_cart.quantity, 'cart_amount': get_cart_ammounts(request)})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'This food does not exist'})
            
        return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})
    
    return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})


def decrease_cart(request):
    if request.user.is_authenticated:
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest': 
            food_id = request.GET.get('food_id')
            try:
                fooditem = FoodItem.objects.get(id=int(food_id))
                try:
                    check_cart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    if check_cart.quantity > 1:
                        check_cart.quantity -= 1
                        check_cart.save()
                    else:
                        check_cart.delete()
                        check_cart.quantity = 0
                    return JsonResponse({'status': 'Success', 'message': 'Incresed the cart quantity', 'cart_counter': get_cart_count(request), 'qty': check_cart.quantity, 'cart_amount': get_cart_ammounts(request)})
                except:
                    return JsonResponse({'status': 'Failed', 'message': "You don't have item in your cart"})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'This food does not exist'})
            
        return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})
    
    return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})    


@login_required(login_url = 'login')
def cart(request):
    context = {}
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    context['cart_items'] = cart_items
    return render(request,'marketplace/cart.html', context)


def delete_cart(request, cart_id=None):
    
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest': 
            food_id = request.GET.get('food_id')
            try:
                cart = Cart.objects.get(user=request.user, id=cart_id)
                if cart:
                    cart.delete()
                    return JsonResponse({'status': 'Success', 'message': 'Cart item has been deleted', 'cart_counter': get_cart_count(request), 'cart_amount': get_cart_ammounts(request)})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'Cart item does not exist'})
        return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})