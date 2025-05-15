from django.urls import path
from . import views

app_name = 'shop'  # вот это важно для namespace!

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('categories/', views.category_list, name='category_list'),
    path('order/<int:pk>/', views.order_detail, name='order_detail'),
    path('search/', views.product_search, name='product_search'),
]
