from django.shortcuts import render
from .models import Vendor

def vendor_profile(request):
    # context = dict()
    # vendor = Vendor.objects.get(user=request.user)
    # context['vendor'] = vendor
    return render(request,'vendor/vendor_profile.html')