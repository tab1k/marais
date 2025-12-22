from django.db import models
from django.conf import settings
from catalog.models import Product

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Пользователь")
    session_key = models.CharField("Сессия", max_length=40, null=True, blank=True)
    total_price = models.DecimalField("Итоговая сумма", max_digits=10, decimal_places=0, default=0)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    status = models.CharField("Статус", max_length=20, default='new', choices=[
        ('new', 'Новый'),
        ('waiting_payment', 'Ожидание оплаты'),
        ('purchased', 'Покупка (Оплачено)'),
        ('cancelled', 'Отмена'),
        ('sent', 'Отправлен в WhatsApp'),
    ])
    discount_amount = models.DecimalField("Сумма скидки", max_digits=10, decimal_places=0, default=0)
    bonuses_used = models.PositiveIntegerField("Использовано бонусов", default=0)
    final_price = models.DecimalField("Итого к оплате", max_digits=10, decimal_places=0, default=0)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ #{self.id} от {self.created_at.strftime('%d.%m.%Y %H:%M')}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name="Товар")
    quantity = models.PositiveIntegerField("Количество", default=1)
    price = models.DecimalField("Цена за единицу", max_digits=10, decimal_places=0)
    size = models.CharField("Размер", max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self):
        return f"{self.product.title} (x{self.quantity})"

    def get_cost(self):
        return self.price * self.quantity

