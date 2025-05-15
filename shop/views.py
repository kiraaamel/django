from django.shortcuts import render
from .models import Product, ProductCategory, Order
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import render, get_object_or_404
from django.db.models import Count


def home(request):
    popular_products = Product.objects.annotate(
        total_sold=Coalesce(Sum('order_items__quantity'), Value(0))
    ).order_by('-total_sold')[:5]

    new_categories = ProductCategory.objects.order_by('-created_at')[:5]
    latest_orders = Order.objects.order_by('-date_ordered')[:5]
    all_categories = ProductCategory.objects.all()

    context = {
        'popular_products': popular_products,
        'new_categories': new_categories,
        'latest_orders': latest_orders,
        'all_categories': all_categories,
    }
    return render(request, 'home.html', context)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})

def category_list(request):
    categories = ProductCategory.objects.annotate(
        product_count=Count('products', distinct=True),  # Кол-во товаров в категории
        ordered_items_count=Count('products__order_items', distinct=True),  # Кол-во заказанных позиций
        total_quantity_ordered=Sum('products__order_items__quantity'),  # Суммарное кол-во заказанных товаров
    )
    return render(request, 'category_list.html', {'categories': categories})

def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'order_detail.html', {'order': order})

def product_search(request):
    query = request.GET.get('query', '')
    category_id = request.GET.get('category')
    products = Product.objects.all()
    if query:
        products = products.filter(name__icontains=query)
    if category_id:
        products = products.filter(category_id=category_id)
    return render(request, 'product_search.html', {'products': products, 'query': query})
