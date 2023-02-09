from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.market_place, name='market_place'),
    path('<slug:vendor_slug>/', views.vendor_detail, name='vendor_detail'),

    # add to cart
    path('add-to-cart', views.add_to_cart, name='add_to_cart'),

    # decrease cart
    path('decrease-cart', views.decrease_cart, name='decrease_cart'),

    # my cart
    path('food/cart/', views.cart, name='cart'),

    # delete cart item
    path('delete_cart/<int:cart_id>', views.delete_cart, name='delete_cart')
    
]
