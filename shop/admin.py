from django.contrib import admin
from .models import ProductCategory, Product, Order, Client, Employee, Payment, OrderItem

# Категории товаров
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    list_filter = ('name',)
    search_fields = ('name',)
    date_hierarchy = 'created_at'

admin.site.register(ProductCategory, ProductCategoryAdmin)

# Товары
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'price', 'category', 'brand', 'size', 'gender',
        'stock_quantity', 'sold_quantity', 'remaining_stock', 'created_by', 'is_in_stock'
    )
    list_filter = ('category', 'brand', 'gender')
    search_fields = ('name', 'description', 'brand')
    raw_id_fields = ('category', 'created_by')
    list_display_links = ('name',)
    readonly_fields = ('sold_quantity', 'remaining_stock')

    @admin.display(description='В наличии')
    def is_in_stock(self, obj):
        return obj.remaining_stock > 0
admin.site.register(Product, ProductAdmin)

# Inline для платежей
class PaymentInline(admin.StackedInline):
    model = Payment
    can_delete = False
    readonly_fields = ('payment_date', 'amount')
    extra = 0

# Inline для товаров в заказе
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('added_to_cart_date',)

# Заказы
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'date_ordered', 'status', 'total_price', 'date_received')
    list_filter = ('status', 'client')
    search_fields = ('client__name',)
    date_hierarchy = 'date_ordered'
    readonly_fields = ['total_price']
    inlines = [OrderItemInline, PaymentInline]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        order = form.instance
        order.total_price = order.calculate_total_price()
        order.save()
        payments = Payment.objects.filter(order=order)
        for payment in payments:
            payment.amount = order.total_price
            payment.save()
admin.site.register(Order, OrderAdmin)

# Клиенты
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number')
    list_filter = ('name', 'email')
    search_fields = ('name', 'email')
    list_display_links = ('name',)

admin.site.register(Client, ClientAdmin)

# Сотрудники
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'hire_date')
    list_filter = ('position',)
    search_fields = ('name', 'position')
    date_hierarchy = 'hire_date'

admin.site.register(Employee, EmployeeAdmin)

# Платежи
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'payment_date', 'amount', 'payment_method')
    list_filter = ('payment_method',)
    search_fields = ('order__id', 'payment_method')
    readonly_fields = ['payment_date']

admin.site.register(Payment, PaymentAdmin)
