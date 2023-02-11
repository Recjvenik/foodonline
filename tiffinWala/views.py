from django.shortcuts import render
from vendor.models import Vendor
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D 
from django.contrib.gis.db.models.functions import Distance


def get_or_set_current_location(request):
    if 'lat' in request.session:
        lat = request.session.get('lat')
        lng = request.session.get('lng')
        return lng, lat
    elif 'lat' in request.GET:
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        request.session['lat'] = lat
        request.session['lng'] = lng
        return lng, lat
    return None


def home_view(request):
    context = dict()
    
    if get_or_set_current_location(request):
        point = GEOSGeometry('POINT(%s %s)'%(get_or_set_current_location(request)), srid=4326)
        vendors = Vendor.objects.filter(user_profile__location__distance_lte=(point, 10000)).annotate(distance=Distance('user_profile__location', point)).order_by('distance')
        for vendor in vendors:
            vendor.kms = round(vendor.distance *100, 1)
    else:
        vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]

    context['vendors'] = vendors
    return render(request, 'home.html', context)