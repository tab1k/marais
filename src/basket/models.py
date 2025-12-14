import uuid

from django.conf import settings
from django.db import models


class Cart(models.Model):
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='carts')
  session_key = models.CharField(max_length=40, blank=True, db_index=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    verbose_name = 'Корзина'
    verbose_name_plural = 'Корзины'

  def __str__(self):
    owner = self.user.email if self.user else self.session_key or 'anonymous'
    return f'Cart #{self.id} ({owner})'

  @property
  def total_quantity(self):
      return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
  cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
  product = models.ForeignKey('catalog.Product', related_name='cart_items', on_delete=models.CASCADE)
  quantity = models.PositiveIntegerField(default=1)
  price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
  size = models.CharField(max_length=50, blank=True, null=True)
  added_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    verbose_name = 'Позиция в корзине'
    verbose_name_plural = 'Позиции в корзине'
    unique_together = ('cart', 'product', 'size')

  def __str__(self):
    return f'{self.product} x {self.quantity}'


class Order(models.Model):
  STATUS_CHOICES = [
    ('new', 'Новый'),
    ('paid', 'Оплачен'),
    ('shipped', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('cancelled', 'Отменен'),
  ]

  PAYMENT_CHOICES = [
    ('card', 'Оплата картой'),
    ('cash', 'Оплата при получении'),
  ]

  DELIVERY_CHOICES = [
    ('courier', 'Курьер'),
    ('pickup', 'Самовывоз'),
  ]

  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
  order_number = models.CharField(max_length=20, unique=True, editable=False)
  status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
  payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='card')
  delivery_method = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='courier')
  full_name = models.CharField(max_length=200)
  email = models.EmailField()
  phone = models.CharField(max_length=32, blank=True)
  address = models.CharField(max_length=255, blank=True)
  city = models.CharField(max_length=120, blank=True)
  comment = models.TextField(blank=True)
  items_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
  delivery_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
  discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
  total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    verbose_name = 'Заказ'
    verbose_name_plural = 'Заказы'
    ordering = ['-created_at']

  def __str__(self):
    return self.order_number

  def save(self, *args, **kwargs):
    if not self.order_number:
      self.order_number = f'ORD-{uuid.uuid4().hex[:8].upper()}'
    super().save(*args, **kwargs)


class OrderItem(models.Model):
  order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
  product = models.ForeignKey('catalog.Product', related_name='order_items', on_delete=models.SET_NULL, null=True, blank=True)
  title = models.CharField(max_length=200)
  price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
  quantity = models.PositiveIntegerField(default=1)
  size = models.CharField(max_length=50, blank=True, null=True)

  class Meta:
    verbose_name = 'Позиция заказа'
    verbose_name_plural = 'Позиции заказов'

  def __str__(self):
    return f'{self.title} x {self.quantity}'

# Create your models here.
