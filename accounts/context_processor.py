from vendor.models import Vendor
from django.conf import settings

def get_vendor(request):
    context = dict()
    try:
        vendor = Vendor.objects.get(user=request.user)
        context['vendor'] = vendor
    except Exception as e:
        print(e)
    
    return context

def get_google_api(request):
    return {'GOOGLE_API_KEY': settings.GOOGLE_API_KEY}