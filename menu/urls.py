from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu_list, name='menu'),
    path('item/<slug:slug>/', views.item_detail, name='item_detail'),
]
