from django.db import models
from decimal import Decimal


class Category(models.Model):
  name = models.CharField(max_length=150, unique=True)
  slug = models.SlugField(max_length=160, unique=True)
  parent = models.ForeignKey('self', related_name='children', on_delete=models.SET_NULL, null=True, blank=True)
  description = models.TextField(blank=True)
  image = models.ImageField(upload_to='categories/', blank=True, null=True)

  class Meta:
    verbose_name = 'Категория'
    verbose_name_plural = 'Категории'
    ordering = ['name']

  def __str__(self):
    return self.name


class Collection(models.Model):
  name = models.CharField(max_length=150, unique=True)
  slug = models.SlugField(max_length=160, unique=True)
  description = models.TextField(blank=True)
  hero_image = models.ImageField(upload_to='collections/', blank=True, null=True)

  class Meta:
    verbose_name = 'Коллекция'
    verbose_name_plural = 'Коллекции'
    ordering = ['name']

  def __str__(self):
    return self.name


class Product(models.Model):
  category = models.ForeignKey(Category, related_name='products', on_delete=models.SET_NULL, null=True, blank=True)
  collection = models.ForeignKey(Collection, related_name='products', on_delete=models.SET_NULL, null=True, blank=True)
  brand_ref = models.ForeignKey('Brand', related_name='products', on_delete=models.SET_NULL, null=True, blank=True)
  brand = models.CharField(max_length=120, blank=True)
  title = models.CharField(max_length=200)
  slug = models.SlugField(max_length=220, unique=True)
  description = models.TextField(blank=True)
  price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
  currency = models.CharField(max_length=8, default='₸')
  discount_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Скидка (%)')
  metal = models.CharField(max_length=100, blank=True)
  material = models.CharField(max_length=150, blank=True)
  coverage = models.CharField(max_length=100, blank=True)
  stones = models.CharField(max_length=200, blank=True)
  color = models.CharField(max_length=80, blank=True)
  weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name='Вес (г)')
  article = models.CharField(max_length=120, blank=True, verbose_name='Артикул')
  size = models.CharField(max_length=50, blank=True)
  stock = models.PositiveIntegerField(default=0)
  is_active = models.BooleanField(default=True)
  main_image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name='Главное фото (файл)')
  main_image_url = models.URLField(max_length=500, blank=True, verbose_name='Главное фото (ссылка)', help_text='Или укажите URL изображения вместо загрузки файла')
  related_colors = models.ManyToManyField('self', blank=True, symmetrical=False, verbose_name="Варианты (другие цвета)")
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    verbose_name = 'Товар'
    verbose_name_plural = 'Товары'
    ordering = ['-created_at']

  def __str__(self):
    return self.title

  @property
  def get_main_image_url(self):
    """Returns the main image URL - from URL field or uploaded file"""
    if self.main_image_url:
      return self.main_image_url
    try:
      if self.main_image:
        return self.main_image.url
    except ValueError:
       pass
    return None

  @property
  def has_main_image(self):
    """Check if product has main image (file or URL)"""
    return bool(self.main_image_url or self.main_image)

  @property
  def has_discount(self):
    try:
      return self.discount_percent is not None and Decimal(self.discount_percent) > 0
    except Exception:
      return False

  @property
  def final_price(self):
    """Returns price with applied discount if present."""
    if self.has_discount:
      try:
        return (self.price * (Decimal('1') - (Decimal(self.discount_percent) / Decimal('100')))).quantize(Decimal('0.01'))
      except Exception:
        return self.price
    return self.price


class ProductImage(models.Model):
  product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
  image = models.ImageField(upload_to='products/gallery/', blank=True, null=True, verbose_name='Фото (файл)')
  image_url = models.URLField(max_length=500, blank=True, verbose_name='Фото (ссылка)', help_text='Или укажите URL изображения вместо загрузки файла')
  alt = models.CharField(max_length=200, blank=True)
  sort_order = models.PositiveIntegerField(default=0)

  class Meta:
    verbose_name = 'Фото товара'
    verbose_name_plural = 'Фото товаров'
    ordering = ['sort_order', 'id']

  def __str__(self):
    return f'{self.product.title} — {self.id}'

  @property
  def get_image_url(self):
    """Returns the image URL - from URL field or uploaded file"""
    if self.image_url:
      return self.image_url
    try:
      if self.image:
        return self.image.url
    except ValueError:
      pass
    return None

  @property
  def has_image(self):
    """Check if has image (file or URL)"""
    return bool(self.image_url or self.image)


class Brand(models.Model):
  name = models.CharField(max_length=200, unique=True)
  slug = models.SlugField(max_length=220, unique=True, blank=True)
  country = models.CharField(max_length=120, blank=True)
  logo = models.ImageField(upload_to='brands/', blank=True, null=True)
  banner = models.ImageField(upload_to='brands/banners/', blank=True, null=True, verbose_name='Баннер')
  description = models.TextField(blank=True)
  is_active = models.BooleanField(default=True)
  sort_order = models.PositiveIntegerField(default=0)

  class Meta:
    verbose_name = 'Бренд'
    verbose_name_plural = 'Бренды'
    ordering = ['sort_order', 'name']

  def __str__(self):
    return self.name

  def save(self, *args, **kwargs):
    if not self.slug:
      from django.utils.text import slugify
      self.slug = slugify(self.name)
    super().save(*args, **kwargs)

  @property
  def active_products(self):
    return self.products.filter(is_active=True)


class HomepageBlock(models.Model):
    BLOCK_TYPES = (
        ('hero', 'Главный Hero'),
        ('brand', 'Блок Бренда'),
        ('banner', 'Баннер'),
    )

    block_type = models.CharField(max_length=20, choices=BLOCK_TYPES, default='brand')
    title = models.CharField(max_length=200, blank=True)
    subtitle = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='blocks/', help_text="Для бренда - фото слева, для баннера - фон")
    link_url = models.CharField(max_length=500, blank=True, help_text="Только для баннеров")
    
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    featured_product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='featured_in_blocks')
    
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    sort_order = models.IntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = 'Блок главной страницы'
        verbose_name_plural = 'Блоки главной страницы'
        ordering = ['sort_order']

    def __str__(self):
        return f"{self.get_block_type_display()}: {self.title or self.brand}"


class Review(models.Model):
    STATUS_CHOICES = (
        ('pending', 'На модерации'),
        ('approved', 'Одобрен'),
        ('rejected', 'Отклонен'),
    )
    
    name = models.CharField(max_length=100, verbose_name="Имя")
    city = models.CharField(max_length=100, verbose_name="Город")
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name="Оценка")
    text = models.TextField(verbose_name="Текст отзыва")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.city}) - {self.rating}★"

    @property
    def stars_display(self):
        """
        Returns a string like '★★★☆☆' so templates don't need to loop for stars.
        Keeps rating clamped between 0 and 5 to avoid rendering errors.
        """
        rating = max(0, min(int(self.rating or 0), 5))
        return '★' * rating + '☆' * (5 - rating)


class SiteSettings(models.Model):
    is_snow_enabled = models.BooleanField(default=False, verbose_name="Включить эффект снега")

    class Meta:
        verbose_name = 'Настройки сайта'
        verbose_name_plural = 'Настройки сайта'

    def __str__(self):
        return "Настройки сайта"

    def save(self, *args, **kwargs):
        # Allow only one instance
        if not self.pk and SiteSettings.objects.exists():
            return
        super(SiteSettings, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
