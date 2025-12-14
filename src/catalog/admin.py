from django.contrib import admin

from .models import Category, Collection, Product, ProductImage, Brand


class ProductImageInline(admin.TabularInline):
  model = ProductImage
  extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
  list_display = ('title', 'price', 'currency', 'is_active', 'category', 'collection', 'stock')
  list_filter = ('is_active', 'category', 'collection')
  search_fields = ('title', 'description', 'slug', 'brand', 'material', 'size')
  prepopulated_fields = {'slug': ('title',)}
  inlines = [ProductImageInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
  list_display = ('name', 'parent')
  search_fields = ('name', 'slug')
  prepopulated_fields = {'slug': ('name',)}


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
  list_display = ('name',)
  search_fields = ('name', 'slug')
  prepopulated_fields = {'slug': ('name',)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
  list_display = ('name', 'country', 'is_active', 'sort_order')
  list_filter = ('is_active',)
  search_fields = ('name', 'country', 'description')
