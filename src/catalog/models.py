from django.db import models


class Category(models.Model):
  name = models.CharField(max_length=150, unique=True)
  slug = models.SlugField(max_length=160, unique=True)
  parent = models.ForeignKey('self', related_name='children', on_delete=models.SET_NULL, null=True, blank=True)
  description = models.TextField(blank=True)

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
  brand = models.CharField(max_length=120, blank=True)
  title = models.CharField(max_length=200)
  slug = models.SlugField(max_length=220, unique=True)
  description = models.TextField(blank=True)
  price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
  currency = models.CharField(max_length=8, default='₸')
  metal = models.CharField(max_length=100, blank=True)
  material = models.CharField(max_length=150, blank=True)
  coverage = models.CharField(max_length=100, blank=True)
  stones = models.CharField(max_length=200, blank=True)
  color = models.CharField(max_length=80, blank=True)
  size = models.CharField(max_length=50, blank=True)
  stock = models.PositiveIntegerField(default=0)
  is_active = models.BooleanField(default=True)
  main_image = models.ImageField(upload_to='products/', blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    verbose_name = 'Товар'
    verbose_name_plural = 'Товары'
    ordering = ['-created_at']

  def __str__(self):
    return self.title


class ProductImage(models.Model):
  product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
  image = models.ImageField(upload_to='products/gallery/')
  alt = models.CharField(max_length=200, blank=True)
  sort_order = models.PositiveIntegerField(default=0)

  class Meta:
    verbose_name = 'Фото товара'
    verbose_name_plural = 'Фото товаров'
    ordering = ['sort_order', 'id']

  def __str__(self):
    return f'{self.product.title} — {self.id}'


class Brand(models.Model):
  name = models.CharField(max_length=200, unique=True)
  country = models.CharField(max_length=120, blank=True)
  logo = models.ImageField(upload_to='brands/', blank=True, null=True)
  description = models.TextField(blank=True)
  is_active = models.BooleanField(default=True)
  sort_order = models.PositiveIntegerField(default=0)

  class Meta:
    verbose_name = 'Бренд'
    verbose_name_plural = 'Бренды'
    ordering = ['sort_order', 'name']

  def __str__(self):
    return self.name
