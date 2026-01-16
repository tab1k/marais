
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marais.settings.development')
django.setup()

from catalog.models import Product, Brand

def check_images():
    total_products = Product.objects.count()
    with_image = Product.objects.exclude(main_image='').count()
    without_image = Product.objects.filter(main_image='').count()

    print(f"Total Products: {total_products}")
    print(f"With Main Image: {with_image}")
    print(f"Without Main Image: {without_image}")

    print("\n--- Products without images by Brand ---")
    brands = Brand.objects.all()
    for brand in brands:
        count = Product.objects.filter(brand_ref=brand, main_image='').count()
        if count > 0:
            has_logo = "Yes" if brand.logo else "NO"
            print(f"{brand.name}: {count} missing images (Brand Logo: {has_logo})")

    # Sample of filenames for verification
    print("\n--- Sample of existing images ---")
    for p in Product.objects.exclude(main_image='')[:5]:
        print(f"{p.title}: {p.main_image.name}")

if __name__ == '__main__':
    check_images()
