from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),              # список товаров
    path('product/add/', views.product_add, name='product_add'),             # добавление
    path('product/<int:pk>/', views.product_detail, name='product_detail'),  # детали
    path('product/<int:pk>/edit/', views.product_edit, name='product_edit'), # редактирование
    path('product/<int:pk>/delete/', views.product_delete, name='product_delete'), # удаление
    path('categories/', views.category_list, name='category_list'),
    path('order/<int:pk>/', views.order_detail, name='order_detail'),
    path('search/', views.product_search, name='product_search'),
]
