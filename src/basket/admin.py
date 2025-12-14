from django.contrib import admin

from .models import Cart, CartItem, Order, OrderItem


class CartItemInline(admin.TabularInline):
  model = CartItem
  extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
  list_display = ('id', 'user', 'session_key', 'created_at', 'updated_at')
  search_fields = ('session_key', 'user__email', 'user__username')
  inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
  model = OrderItem
  extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
  list_display = ('order_number', 'status', 'full_name', 'email', 'total', 'created_at')
  list_filter = ('status', 'payment_method', 'delivery_method')
  search_fields = ('order_number', 'full_name', 'email', 'phone')
  inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
  list_display = ('order', 'title', 'price', 'quantity')
