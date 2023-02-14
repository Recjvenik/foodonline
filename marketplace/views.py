from django.shortcuts import get_object_or_404, render, redirect
from vendor.models import Vendor, BusinessHour
from menu.models import Category, FoodItem
from .models import Cart
from .context_processor import get_cart_count, get_cart_ammounts
from django.db.models import Prefetch
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required 
from django.db.models import Q
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D 
from django.contrib.gis.db.models.functions import Distance
from datetime import date
from orders.forms import OrderForm
from accounts.models import UserProfile
# Create your views here.

def market_place(request):
    context = {}
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    context['vendor_count'] = vendor_count
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
    business_hours = BusinessHour.objects.filter(vendor=vendor).order_by('day', '-from_hour')
    
    today = date.today().isoweekday()
    current_business_hour = BusinessHour.objects.filter(vendor=vendor, day=today)

    cart_item= None
    if request.user.is_authenticated:
        cart_item = Cart.objects.filter(user=request.user)
    
        context['cart_item'] = cart_item
    context['vendor'] = vendor
    context['categories'] = categories
    context['business_hours'] = business_hours
    context['current_business_hour'] = current_business_hour
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
    

def search(request):
    context = {}
    address = request.GET.get('address')
    latitude = request.GET.get('lat')
    longitude = request.GET.get('lng')
    radius = request.GET.get('radius')
    keyword = request.GET.get('keyword')

    if not address:
        return redirect('market_place')
    fetch_vendors_by_food_items = FoodItem.objects.filter(food_title__icontains=keyword, is_available=True).values_list('vendor', flat=True)
    vendors = Vendor.objects.filter(Q(id__in=fetch_vendors_by_food_items) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True))
    if latitude and longitude:
        point = GEOSGeometry('POINT(%s %s)'%(longitude, latitude), srid=4326)
        vendors = Vendor.objects.filter(Q(id__in=fetch_vendors_by_food_items) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True),
                                         user_profile__location__distance_lte=(point, radius)).annotate(distance=Distance('user_profile__location', point)).order_by('distance')
        
        for vendor in vendors:
            vendor.kms = round(vendor.distance *100, 1)
    vendor_count = vendors.count()
    context['vendor_count'] = vendor_count
    context['vendors'] = vendors
    context['search_location'] = address
    return render(request, 'marketplace/market_listings.html', context)

@login_required(login_url='login')
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    
    if cart_count < 1:
        return redirect('market_place')
    
    user_profile = UserProfile.objects.get(user=request.user)
    initial = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'phone': request.user.phone_number,
        'email': request.user.email,
        'address': user_profile.address,
        'country': user_profile.country,
        'state': user_profile.state,
        'city': user_profile.city,
        'pin_code': user_profile.pin_code,
    }

    form = OrderForm(request.POST or None, initial=initial)
    
    
    context = {
        'form': form,
        'cart_items': cart_items
    }
    return render(request, 'marketplace/checkout.html', context)