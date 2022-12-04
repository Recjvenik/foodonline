from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UserForm
from vendor.forms import VendorForm
from .models import User, UserProfile
from django.contrib import messages, auth
from django.template.defaultfilters import slugify
from .utils import detectUser
from django.contrib.auth.decorators import login_required, user_passes_test

from django.core.exceptions import PermissionDenied



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
            messages.success(request, 'Your account has been created successfully...')
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
            messages.success(request, 'Your account has been created successfully...!!')
            return redirect('register-vendor')
        else:
            print('invalid form')
            print(form.errors)
            print(v_form.errors)
    context['form'] = form
    context['v_form'] = v_form
    return render(request, 'accounts/register-vendor.html', context)


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
def customerDashboard(request):
    context = dict()
    return render(request, 'accounts/customer-dashboard.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    context = dict()
    return render(request, 'accounts/vendor-dashboard.html', context)
