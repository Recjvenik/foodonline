from django.urls import path, include
from . import views
from accounts import views as AccountViews

urlpatterns = [
    path('', AccountViews.vendorDashboard, name='vendor'),
    path('profile', views.vendor_profile, name='vendor_profile'),
    path('menu-builder', views.menu_builder, name='menu_builder'),
    path('menu-builder/category/<int:pk>', views.fooditems_by_category, name='fooditems_by_category'),

    # category crud
    path('menu-builder/category/add/', views.add_edit_category, name='add_edit_category'),
    path('menu-builder/category/edit/<int:pk>/', views.add_edit_category, name='add_edit_category'),
    path('menu-builder/category/delete/<int:pk>/', views.delete_category, name='delete_category')
]