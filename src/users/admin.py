from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
  fieldsets = UserAdmin.fieldsets + (
    ('Дополнительно', {'fields': ('phone', 'loyalty_points', 'discount_percent', 'avatar')}),
  )
  add_fieldsets = UserAdmin.add_fieldsets + (
    ('Дополнительно', {'fields': ('phone', 'loyalty_points', 'discount_percent', 'avatar')}),
  )
  list_display = ('username', 'email', 'first_name', 'last_name', 'phone', 'loyalty_points', 'discount_percent', 'is_staff')
  search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
