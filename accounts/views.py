from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UserForm
from vendor.forms import VendorForm
from .models import User, UserProfile
from django.contrib import messages, auth
from django.template.defaultfilters import slugify
from .utils import detectUser, send_verification_mail
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.http import urlsafe_base64_decode
from django.core.exceptions import PermissionDenied
from django.contrib.auth.tokens import default_token_generator
from vendor.models import Vendor
from orders.models import Order
from datetime import datetime

def check_role_vendor(user):
    if user.role == 1:
        return True
    raise PermissionDenied


def check_role_customer(user):
    if user.role == 2:
        return True
    raise PermissionDenied


def registerUser(request):
    context = dict()
    form = UserForm()
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('my-account')
    elif request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():

            # print(form.cleaned_data)
            # user = form.save(commit=False)
            # user.role = User.CUSTOMER
            # form.save()
            
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.role = User.CUSTOMER
            user.save()
            
            # send verification mail
            mail_subject = 'Please activate your account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_mail(request, user, mail_subject, email_template)
            
            messages.success(request, 'Your account has been created successfully. Pleae activate your acount via email.')
            return redirect('register-user')
            
    context['form'] = form
    return render(request, 'accounts/register.html', context)


def registerVendor(request):
    context = dict()
    form = UserForm(request.POST or None)
    v_form = VendorForm(request.POST, request.FILES or None)
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('my-account')
    elif request.method == 'POST':
        if form.is_valid() and v_form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.role = User.VENDOR
            user.save()
            vendor = v_form.save(commit=False)
            vendor.user = user
            vendor_name = v_form.cleaned_data['vendor_name']
            vendor.vendor_slug = slugify(vendor_name)+'-'+str(user.id)
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()

            mail_subject = 'Please activate your account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_mail(request, user, mail_subject, email_template)
            
            messages.success(request, 'Your account has been created successfully. Pleae activate your acount via email.')
            return redirect('register-vendor')
        else:
            print('invalid form')
            print(form.errors)
            print(v_form.errors)
    context['form'] = form
    context['v_form'] = v_form
    return render(request, 'accounts/register-vendor.html', context)


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congretulations, your account is acrivated')
    else:
        messages.error(request, 'Invalid activation link')
    return redirect('my-account')

def login(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('my-account')
    elif request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        print(email, password)
        user = auth.authenticate(email=email, password=password)
        print('user: ',user)
        if user is not None:
            print('test 1')
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('my-account')
        else:
            print('test 2')
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'accounts/login.html')


def logout(request):
    auth.logout(request)
    messages.info(request, 'You are logged out.')
    return redirect('login')


@login_required(login_url='login')
def myAccount(request):
    user = request.user
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)


@login_required(login_url='login')
@user_passes_test(check_role_customer)
def customer_dashboard(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    recent_orders = orders[:5]
    context = {
        'orders': orders,
        'orders_count': orders.count(),
        'recent_orders': recent_orders,
    }
    return render(request, 'accounts/customer-dashboard.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendor_dashboard(request):
    vendor = Vendor.objects.get(user=request.user)
    orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by('-created_at')
    recent_orders = orders[:5]
    
    current_mont_revenue = 0
    current_month = datetime.now().month
    current_month_orders = orders.filter(vendors__in=[vendor.id], created_at__month=current_month)
    for order in current_month_orders:
        current_mont_revenue += order.get_total_by_vendor()['grand_total']
    
    total_revenue = 0
    for order in orders:
        total_revenue += order.get_total_by_vendor()['grand_total']
    
    context = {
        'vendor': vendor,
        'recent_orders': recent_orders,
        'orders_count': orders.count(),
        'total_revenue': total_revenue,
        'current_mont_revenue': current_mont_revenue
    }
    return render(request, 'accounts/vendor-dashboard.html', context)


def forget_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)
            mail_subject = 'Reset your password'
            email_template = 'accounts/emails/reset_password_email.html'
            send_verification_mail(request, user, mail_subject, email_template) 
            messages.success(request, 'Password reset link has been sent to your email address.')
            return redirect('login')
        else:
            messages.warning(request, 'Account does not exist with this email.')
            return redirect('forget_password')
    return render(request, 'accounts/forget_password.html')


def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, 'Please, reset your passwotrd')
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has been expired')
        return redirect('my-account')
    

def reset_password(request):
    print(request.POST, )
    if request.method=='POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, 'Passwotrd reset successfull')
            return redirect('login')
        else:
            messages.error(request, 'Password does not match')
            return redirect('reset_password')
    return render(request, 'accounts/reset_password.html')