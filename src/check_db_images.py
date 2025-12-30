import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marais.settings')
django.setup()

from catalog.models import Product

products = Product.objects.filter(is_active=True)[:5]
for p in products:
    print(f"Product: {p.title} ({p.article})")
    print(f"  Main Image URL: '{p.main_image_url}'")
    print(f"  get_main_image_url: '{p.get_main_image_url}'")
    for img in p.images.all():
        print(f"  Extra Image: '{img.image_url}'")
    print("-" * 20)
