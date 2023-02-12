from vendor.models import Vendor
from django.conf import settings
from .models import UserProfile

def get_vendor(request=None):
    context = dict()
    try:
        if request.user.is_authenticated:
            vendor = Vendor.objects.get(user=request.user)
            context['vendor'] = vendor
    except Exception as e:
        print(e)
    
    return context


def get_user_profile(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except:
        user_profile = None
    return dict(user_profile=user_profile)

def get_google_api(request):
    return {'GOOGLE_API_KEY': settings.GOOGLE_API_KEY}