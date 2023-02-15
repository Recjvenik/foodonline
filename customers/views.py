from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.models import User, UserProfile
from accounts.forms import UserProfileForm, UserInfoForm
from django.shortcuts import get_object_or_404
from django.contrib import messages
from orders.models import Order, OrderedFood
import simplejson as json
# Create your views here.

@login_required(login_url='login')
def customer_profile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    profile_form = UserProfileForm(request.POST or None, request.FILES or None, instance=profile)
    user_info_form = UserInfoForm(request.POST or None, instance=request.user)

    if request.method == 'POST':
        if profile_form.is_valid() and user_info_form.is_valid():
            profile_form.save()
            user_info_form.save()
            messages.success(request, 'Profile Updated!')
            return redirect('customer_profile')
    context = {
        'profile_form': profile_form,
        'user_info_form': user_info_form,
        'profile': profile,
    }
    return render(request, 'customers/customer_profile.html', context)

def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'customers/my_orders.html', context)


def order_details(request, order_number=None):
    try:
        order = Order.objects.get(order_number=order_number)
        ordered_food = OrderedFood.objects.filter(order=order)
        subtotal = 0
        for item in ordered_food:
            subtotal += (item.price * item.quantity)
        tax_data = json.loads(order.tax_data)
        
        context = {
            'order': order,
            'ordered_food': ordered_food,
            'subtotal': subtotal,
            'tax_data': tax_data
        }
        return render(request, 'customers/order_details.html', context)
    except Exception as e:
        print('order_details: ',e)
        return redirect('customer')
