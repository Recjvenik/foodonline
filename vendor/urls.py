from django.urls import path, include
from . import views
from accounts import views as AccountViews

urlpatterns = [
    path('', AccountViews.vendor_dashboard, name='vendor'),
    path('profile', views.vendor_profile, name='vendor_profile'),
    path('menu-builder', views.menu_builder, name='menu_builder'),
    path('menu-builder/category/<int:pk>', views.fooditems_by_category, name='fooditems_by_category'),

    # category crud
    path('menu-builder/category/add/', views.add_edit_category, name='add_edit_category'),
    path('menu-builder/category/edit/<int:pk>/', views.add_edit_category, name='add_edit_category'),
    path('menu-builder/category/delete/<int:pk>/', views.delete_category, name='delete_category'),

    # fooditem CRUD
    path('menu-builder/category/food/add/', views.add_edit_food_item, name='add_food_item'),
    path('menu-builder/category/<int:category_id>/food/add/', views.add_edit_food_item, name='add_edit_food_item'),
    path('menu-builder/category/<int:category_id>/food/edit/<int:pk>/', views.add_edit_food_item, name='add_edit_food_item'),
    path('menu-builder/food-item/delete/<int:pk>/', views.delete_food_item, name='delete_food_item'),

    # Opening Hour Crud
    path('opening-hours/', views.opening_hours, name='opening_hours'),
    path('opening-hours/add', views.add_opening_hours, name='add_opening_hours'),
    path('opening-hours/remove/<int:pk>', views.remove_opening_hours, name='remove_opening_hours'),
    
    path('order-detail/<slug:order_number>', views.order_detail, name='vendor_order_detail'),

    path('my-orders/', views.my_orders, name='vendor_my_orders'),
]