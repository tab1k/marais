from django.contrib import admin

from .models import Category, Collection, Product, ProductImage, Brand, HomepageBlock, Review


class ProductImageInline(admin.TabularInline):
  model = ProductImage
  extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
  list_display = ('title', 'price', 'currency', 'is_active', 'category', 'collection', 'brand_ref', 'stock')
  list_filter = ('is_active', 'category', 'collection', 'brand_ref')
  search_fields = ('title', 'description', 'slug', 'brand', 'material', 'size', 'brand_ref__name')
  autocomplete_fields = ['related_colors']
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


@admin.register(HomepageBlock)
class HomepageBlockAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'block_type', 'is_active', 'sort_order')
    list_editable = ('is_active', 'sort_order')
    list_filter = ('block_type', 'is_active')
    search_fields = ('title', 'brand__name')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'rating', 'status', 'created_at')
    list_filter = ('status', 'rating', 'created_at')
    list_editable = ('status',)
    search_fields = ('name', 'city', 'text')
    readonly_fields = ('created_at',)
    actions = ['approve_reviews', 'reject_reviews']
    
    def approve_reviews(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} отзывов одобрено.')
    approve_reviews.short_description = 'Одобрить выбранные отзывы'
    
    def reject_reviews(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} отзывов отклонено.')
    reject_reviews.short_description = 'Отклонить выбранные отзывы'

