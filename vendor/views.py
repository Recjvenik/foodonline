from django.shortcuts import render, get_object_or_404, redirect
from .models import Vendor
from .forms import VendorForm
from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_role_vendor

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