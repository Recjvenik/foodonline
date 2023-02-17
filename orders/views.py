from django.shortcuts import render, redirect
from marketplace.models import Cart, Tax
from marketplace.context_processor import get_cart_ammounts
from .forms import OrderForm
from .models import Order, Payment, OrderedFood
import simplejson as json
from .utils import generate_order_number
from django.http import HttpResponse, JsonResponse
from accounts.utils import send_notification
from django.contrib.auth.decorators import login_required
from menu.models import FoodItem
# Create your views here.

@login_required(login_url='login')
def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    
    if cart_count < 1:
        return redirect('market_place')
    
    vendors_ids = list(set([item.fooditem.vendor.id for item in cart_items]))
    get_tax = Tax.objects.filter(is_active=True)
    subtotal = 0
    total_data = {}
    k = {}
    for item in cart_items:
        fooditem = FoodItem.objects.get(pk=item.fooditem.id, vendor_id__in=vendors_ids)
        v_id = fooditem.vendor.id
        if v_id in k:
            subtotal += (fooditem.price * item.quantity)
        else:
            subtotal = (fooditem.price * item.quantity)
        k[v_id] = subtotal

        tax_dict = {}
        for tax in get_tax:
            tax_type = tax.tax_type
            tax_percentage = tax.tax_percentage
            tax_amount = round((tax_percentage * subtotal)/100, 2)
            tax_dict.update({tax_type: {str(tax_percentage): str(tax_amount)}})

        total_data.update({fooditem.vendor.id: {str(subtotal): str(tax_dict)}})




    get_cart_ammount = get_cart_ammounts(request)
    subtotal = get_cart_ammount['subtotal']
    total_tax = get_cart_ammount['tax']
    grand_total = get_cart_ammount['grand_total']
    tax_data = get_cart_ammount['tax_dict']
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            form_data = form.save(commit=False)
            form_data.user = request.user
            form_data.total = grand_total
            form_data.tax_data = json.dumps(tax_data)
            form_data.total_data = json.dumps(total_data)
            form_data.total_tax = total_tax
            form_data.payment_method = request.POST['payment_method']
            form_data.save()
            form_data.order_number = generate_order_number(form_data.id)
            form_data.vendors.add(*vendors_ids)
            form_data.save()
            context = {
                'order': form_data,
                'cart_items': cart_items
            }
            return render(request, 'orders/place_order.html', context)
   
    return render(request, 'orders/place_order.html')


@login_required(login_url='login')
def payments(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        order_number = request.POST.get('order_number')
        transaction_id = request.POST.get('transaction_id')
        payment_method = request.POST.get('payment_method')
        status = request.POST.get('status')

        order = Order.objects.get(user=request.user, order_number=order_number)
        payment = Payment(
            user = request.user,
            transaction_id = transaction_id,
            payment_method = payment_method,
            amount = order.total,
            status = status
        )
        payment.save()

        order.payment = payment
        order.is_ordered = True
        order.save()

        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            ordered_food = OrderedFood()
            ordered_food.order = order
            ordered_food.payment = payment
            ordered_food.user = request.user
            ordered_food.fooditem = item.fooditem
            ordered_food.quantity = item.quantity
            ordered_food.price = item.fooditem.price
            ordered_food.amount = item.fooditem.price * item.quantity
            ordered_food.save()


        # send order confirmation email to customer

        mail_subject = 'Thank you for ordering with us.'
        mail_template = 'orders/order_confirmation_email.html'
        context = {
            'user': request.user,
            'order': order,
            'to_email': order.email
        }
        send_notification(mail_subject, mail_template, context)

        # send order recieved email to vendor

        mail_subject = 'You have recieved a new order.'
        mail_template = 'orders/new_order_received.html'
        to_email = []
        for item in cart_items:
            if item.fooditem.vendor.user.email not in to_email:
                to_email.append(item.fooditem.vendor.user.email)
        context = {
            'order': order,
            'to_email': to_email
        }
        send_notification(mail_subject, mail_template, context)
        
        # clear the cart if payment is success
        # cart_items.delete()
        
        response = {
            'order_number': order_number,
            'transaction_id': transaction_id
        }
        return JsonResponse(response)

    return HttpResponse('Payment view')


def order_complete(request):
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id')
    
    try:
        order = Order.objects.get(order_number=order_number, payment__transaction_id=transaction_id, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order)
        
        subtotal = 0
        for item in ordered_food:
            subtotal += (item.price * item.quantity)
        tax_data = json.loads(order.tax_data)
        context = {
            'order': order,
            'ordered_food': ordered_food,
            'subtotal': subtotal,
            'tax_data': tax_data,
        }
        return render(request, 'orders/order_complete.html', context)
    except Exception as e:
        print(e)
        return redirect('home')