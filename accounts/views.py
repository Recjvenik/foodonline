from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UserForm
from vendor.forms import VendorForm
from .models import User, UserProfile
from django.contrib import messages
from django.template.defaultfilters import slugify

# Create your views here.
def registerUser(request):
    context = dict()
    form = UserForm()
    if request.method == 'POST':
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

    if request.method == 'POST':
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
