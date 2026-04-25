from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_index, name='dashboard'),
    path('orders/', views.dashboard_orders, name='dashboard_orders'),
    path('orders/<int:order_id>/status/', views.update_order_status, name='update_order_status'),
    path('menu/', views.dashboard_menu, name='dashboard_menu'),
    path('menu/<int:item_id>/toggle/', views.toggle_item_availability, name='toggle_item_availability'),
    path('users/', views.dashboard_users, name='dashboard_users'),
    path('users/<int:user_id>/toggle/', views.toggle_user_active, name='toggle_user_active'),
]
