from django import forms
from .models import Vendor, BusinessHour
# from accounts.validators import allow_only_images_validator


class VendorForm(forms.ModelForm):
    vendor_license = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}))
    class Meta:
        model = Vendor
        fields = ['vendor_name', 'vendor_license']


class BusinessHourForm(forms.ModelForm):

    class Meta:
        model = BusinessHour
        fields = ['day', 'from_hour', 'to_hour', 'is_closed']