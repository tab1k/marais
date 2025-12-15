from django.db import models

# Create your models here.

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True, verbose_name='Email')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата подписки')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        ordering = ['-created_at']

    def __str__(self):
        return self.email
