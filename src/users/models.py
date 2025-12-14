from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=32, blank=True)
    loyalty_points = models.PositiveIntegerField(default=0)
    discount_percent = models.PositiveSmallIntegerField(default=0)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return self.username
