from vendor.models import Vendor

def get_vendor(request):
    context = dict()
    try:
        vendor = Vendor.objects.get(user=request.user)
        context['vendor'] = vendor
    except Exception as e:
        print(e)
    
    return context