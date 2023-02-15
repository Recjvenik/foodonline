from django.urls import path, include
from accounts import views as AccountViews
from . import views
urlpatterns = [
    path('', AccountViews.customer_dashboard, name='customer'),
    path('profile/', views.customer_profile, name='customer_profile'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('order-details/<slug:order_number>', views.order_details, name='order_details'),
]