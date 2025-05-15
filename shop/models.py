from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, F
from django.core.exceptions import ValidationError

class ProductCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    description = models.TextField(blank=True, verbose_name="Описание категории")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория товара"
        verbose_name_plural = "Категории товаров"

class Product(models.Model):
    GENDER_CHOICES = [
        ('male', 'Мужской'),
        ('female', 'Женский'),
        ('kids', 'Детский'),
    ]

    name = models.CharField(max_length=200, verbose_name="Название товара")
    description = models.TextField(blank=True, verbose_name="Описание товара")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name="products", verbose_name="Категория")
    stock_quantity = models.PositiveIntegerField(verbose_name="Количество на складе")
    image = models.ImageField(upload_to='product_images/', blank=True, null=True, verbose_name="Изображение")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='unisex', verbose_name="Пол")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Создатель")
    brand = models.CharField(max_length=100, verbose_name="Бренд", default='UnknownBrand')
    size = models.CharField(max_length=50, verbose_name="Размер", default='Unknown')

    @property
    def sold_quantity(self):
        total = sum(item.quantity for item in self.order_items.all())
        return total

    @property
    def remaining_stock(self):
        return self.stock_quantity - self.sold_quantity

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

class Client(models.Model):
    name = models.CharField(max_length=200, verbose_name="Имя клиента")
    email = models.EmailField(unique=True, verbose_name="Электронная почта")
    phone_number = models.CharField(max_length=15, blank=True, verbose_name="Номер телефона")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Клиент")
    date_ordered = models.DateTimeField(auto_now_add=True, verbose_name="Дата заказа")
    status = models.CharField(max_length=50, choices=[('processing', 'В процессе'), ('shipped', 'Отправлен')], verbose_name="Статус")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Общая сумма", default=0)
    date_received = models.DateTimeField(blank=True, null=True, verbose_name="Дата получения")

    def __str__(self):
        return f"Заказ {self.id} от {self.client.name}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def calculate_total_price(self):
        total = self.order_items.aggregate(
            total=Sum(F('quantity') * F('product__price'))
        )['total'] or 0
        return total

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField()
    added_to_cart_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления в корзину")
    ordered = models.BooleanField(default=False, verbose_name="Заказан")

    def __str__(self):
        return f"{self.product.name} в заказе {self.order.id}"

    class Meta:
        verbose_name = "Товар в заказе"
        verbose_name_plural = "Товары в заказах"

    def clean(self):
        if self.product.stock_quantity < self.quantity:
            raise ValidationError(
                f'Недостаточно товара на складе: доступно {self.product.stock_quantity}, запрошено {self.quantity}')

    def save(self, *args, **kwargs):
        self.clean()
        if self.pk is None:
            self.product.stock_quantity -= self.quantity
            if self.product.stock_quantity < 0:
                raise ValidationError('Нельзя уменьшить остаток ниже нуля')
            self.product.save()
        else:
            old = OrderItem.objects.get(pk=self.pk)
            diff = self.quantity - old.quantity
            if self.product.stock_quantity < diff:
                raise ValidationError('Нельзя уменьшить остаток ниже нуля')
            self.product.stock_quantity -= diff
            self.product.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.product.stock_quantity += self.quantity
        self.product.save()
        super().delete(*args, **kwargs)
class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, verbose_name="Заказ")
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата платежа")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма", null=True, blank=True)
    payment_method = models.CharField(max_length=50, choices=[('credit_card', 'Кредитная карта'), ('online', 'Онлайн-оплата')], verbose_name="Метод оплаты")

    def __str__(self):
        return f"Платеж по заказу {self.order.id}"

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"

class Employee(models.Model):
    name = models.CharField(max_length=200, verbose_name="Имя сотрудника")
    position = models.CharField(max_length=100, verbose_name="Должность")
    hire_date = models.DateField(verbose_name="Дата приема на работу")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
