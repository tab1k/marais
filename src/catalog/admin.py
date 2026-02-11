from django import forms
from django.contrib import admin

from .models import Category, Collection, Product, ProductImage, Brand, HomepageBlock, Review


class ProductImageInline(admin.TabularInline):
  model = ProductImage
  extra = 1


class ProductAdminForm(forms.ModelForm):
  size_stock_text = forms.CharField(
    required=False,
    label='Размеры/остатки',
    help_text='Одна строка на размер: например "17=2". Можно несколько строк.',
    widget=forms.Textarea(attrs={'rows': 3}),
  )

  class Meta:
    model = Product
    exclude = ('size_stock',)

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # Pre-fill from existing size_stock_map
    if self.instance and self.instance.pk:
      pairs = []
      for size, qty in self.instance.size_stock_map.items():
        pairs.append(f"{size}={qty}")
      if pairs:
        self.initial['size_stock_text'] = "\n".join(pairs)

  def clean_size_stock_text(self):
    text = self.cleaned_data.get('size_stock_text', '') or ''
    result = {}
    for line in text.splitlines():
      line = line.strip()
      if not line:
        continue
      # allow separators "=" or ":"
      if '=' in line:
        parts = line.split('=', 1)
      elif ':' in line:
        parts = line.split(':', 1)
      else:
        raise forms.ValidationError('Используйте формат "размер=количество", например 17=2')
      size = parts[0].strip()
      qty_raw = parts[1].strip()
      if not size:
        raise forms.ValidationError('Размер не может быть пустым.')
      try:
        qty = int(qty_raw)
      except ValueError:
        raise forms.ValidationError(f'Не удалось прочитать количество "{qty_raw}" для размера {size}')
      result[size] = max(qty, 0)
    # Store parsed result for save()
    self.cleaned_data['_parsed_size_stock'] = result
    return text

  def save(self, commit=True):
    instance = super().save(commit=False)
    parsed = self.cleaned_data.get('_parsed_size_stock', {})
    instance.size_stock = parsed
    if commit:
      instance.save()
      self.save_m2m()
    return instance


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
  list_display = ('title', 'article', 'price', 'discount_percent', 'currency', 'weight', 'is_active', 'category', 'collections_display', 'brand_ref', 'stock', 'size_stock_display')
  list_filter = ('is_active', 'category', 'collections', 'brand_ref')
  search_fields = ('title', 'article', 'description', 'slug', 'brand', 'material', 'size', 'brand_ref__name', 'collections__name')
  autocomplete_fields = ['related_colors', 'collections']
  prepopulated_fields = {'slug': ('title',)}
  inlines = [ProductImageInline]
  form = ProductAdminForm
  exclude = ('size_stock',)

  def collections_display(self, obj):
    return ", ".join(obj.collections.values_list('name', flat=True))
  collections_display.short_description = 'Коллекции'

  def size_stock_display(self, obj):
    if not obj.size_stock_map:
      return ''
    return ", ".join([f"{size}:{qty}" for size, qty in obj.size_stock_map.items()])
  size_stock_display.short_description = 'Размеры/остаток'


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

    reject_reviews.short_description = 'Отклонить выбранные отзывы'


from .models import SiteSettings

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Общее', {'fields': ('is_snow_enabled',)}),
        ('Промо-модалка', {
            'fields': (
                'promo_is_active',
                'promo_image',
                'promo_link',
                'promo_eyebrow',
                'promo_title',
                'promo_text',
            )
        }),
    )

    # Lock down add/delete usually, but for simplicity just basic
    def has_add_permission(self, request):
        # Allow add only if none exists
        if SiteSettings.objects.exists():
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        return False
