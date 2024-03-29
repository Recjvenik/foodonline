from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.myAccount),
    path('register/', views.registerUser, name='register-user'),
    path('register-vendor/', views.registerVendor, name='register-vendor'),
    
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    
    path('my-account/', views.myAccount, name='my-account'),
    path('customer-dashboard/', views.customer_dashboard, name='customer-dashboard'),
    path('vendor-dashboard/', views.vendor_dashboard, name='vendor-dashboard'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),

    path('forget-password/', views.forget_password, name='forget_password'),
    path('reset-password-validate/<uidb64>/<token>/', views.reset_password_validate, name='reset_password_validate'),
    path('reset-password/', views.reset_password, name='reset_password'),
]