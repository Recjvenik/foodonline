from django.shortcuts import render, get_object_or_404, redirect
from .models import Vendor
from .forms import VendorForm
from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_role_vendor
from menu.models import Category, FoodItem
from menu.forms import CategoryForm, FoodItemForm
from django.template.defaultfilters import slugify


def get_vendor(request):
    vendor = Vendor.objects.get(user=request.user)
    return vendor

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendor_profile(request):
    
    context = {}
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)
    profile_form = UserProfileForm(instance=profile)
    vendor_form = VendorForm(instance=vendor)
    
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)

        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, 'Profile Updated Successfully')
            return redirect ('vendor_profile')
        
    context['profile'] = profile
    context['vendor'] = vendor
    context['profile_form'] = profile_form
    context['vendor_form'] = vendor_form
    return render(request,'vendor/vendor_profile.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def menu_builder(request):
    context = {}
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor=vendor).order_by('created_at')
    context['categories'] = categories
    return render(request, 'vendor/menu_builder.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def fooditems_by_category(request, pk=None):
    context = {}
    vendor = get_vendor(request)
    category = get_object_or_404(Category, pk=pk)
    fooditems = FoodItem.objects.filter(vendor=vendor, category=category)
    context['category'] = category
    context['fooditems'] = fooditems
    return render(request, 'vendor/fooditems_by_category.html', context)


def add_edit_category(request, pk=None):
    
    context = {}
    vendor = get_vendor(request)
    category = None
    
    if pk:
        category = get_object_or_404(Category,pk=pk)
    
    form = CategoryForm(request.POST or None, instance=category)
    
    if request.method == 'POST':
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = vendor
            category.save()
            category.slug = slugify(category_name)+'-'+str(category.id)
            category.save()
            messages.success(request, 'Category updated successfully')
            return redirect('menu_builder')
    
    context['form'] = form
    context['category'] = category
    return render(request, 'vendor/add_edit_category.html', context)


def delete_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, 'Category has been deleted successfully')
    return redirect('menu_builder')


def add_edit_food_item(request, category_id=None, pk=None):
    context = {}
    vendor = get_vendor(request)
    category = None
    foodItem = None
    
    if category_id:
        category = get_object_or_404(Category,pk=category_id)
    
    if pk:
        foodItem = get_object_or_404(FoodItem, pk=pk)
    
    form = FoodItemForm(request.POST or None, request.FILES or None, instance=foodItem, category=category)
    form.fields['category'].queryset = Category.objects.filter(vendor=vendor)
    if request.method == 'POST':
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            food_item = form.save(commit=False)
            food_item.vendor = vendor
            food_item.slug = slugify(food_title)
            form.save()
            messages.success(request, 'Category updated successfully')
            return redirect('fooditems_by_category', food_item.category.id)
    
    context['form'] = form
    context['foodItem'] = foodItem
    return render(request, 'vendor/add_edit_food_item.html', context) 


def delete_food_item(request, pk=None):
    food_item = get_object_or_404(FoodItem, pk=pk)
    food_item.delete()
    messages.success(request, 'Food item has been deleted successfully')
    return redirect('fooditems_by_category', food_item.category.id)