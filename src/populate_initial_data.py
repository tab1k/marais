import os
import django
from django.utils.text import slugify

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marais.settings.development')
django.setup()

from catalog.models import Category, Brand, Product

def populate():
    print("Starting population script...")

    # Create Categories
    categories_data = [
        {'name': 'Кольца', 'slug': 'rings'},
        {'name': 'Серьги', 'slug': 'earrings'},
        {'name': 'Ожерелья', 'slug': 'necklaces'},
        {'name': 'Браслеты', 'slug': 'bracelets'},
    ]

    categories = {}
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            slug=cat_data['slug'],
            defaults={'name': cat_data['name']}
        )
        categories[cat_data['slug']] = category
        if created:
            print(f"Created Category: {category.name}")
        else:
            print(f"Category exists: {category.name}")

    # Create Brands
    brands_data = [
        {'name': 'Marais', 'country': 'Kazakhstan'},
        {'name': 'Tiffany & Co.', 'country': 'USA'},
    ]

    brands = {}
    for brand_data in brands_data:
        brand, created = Brand.objects.get_or_create(
            name=brand_data['name'],
            defaults={'country': brand_data['country']}
        )
        brands[brand_data['name']] = brand
        if created:
            print(f"Created Brand: {brand.name}")
        else:
            print(f"Brand exists: {brand.name}")

    # Create Products
    products_data = [
        {
            'title': 'Кольцо "Бриллиантовая искра"',
            'slug': 'diamond-sparkle-ring',
            'category': 'rings',
            'brand': 'Marais',
            'price': 150000.00,
            'description': 'Прекрасное золотое кольцо с бриллиантом.',
            'metal': 'Gold 585',
            'size': '16.0, 16.5, 17.0, 17.5',
        },
        {
            'title': 'Серьги "Золотая петля"',
            'slug': 'golden-loop-earrings',
            'category': 'earrings',
            'brand': 'Marais',
            'price': 85000.00,
            'description': 'Элегантные золотые серьги для повседневной носки.',
            'metal': 'Gold 585',
            'size': '',
        },
        {
            'title': 'Ожерелье "Серебряная цепь"',
            'slug': 'silver-chain-necklace',
            'category': 'necklaces',
            'brand': 'Tiffany & Co.',
            'price': 45000.00,
            'description': 'Стерлинговое серебро, классический дизайн.',
            'metal': 'Silver 925',
            'size': '45cm, 50cm',
        },
        {
            'title': 'Браслет "Шарм"',
            'slug': 'charm-bracelet',
            'category': 'bracelets',
            'brand': 'Tiffany & Co.',
            'price': 120000.00,
            'description': 'Браслет с уникальными шармами.',
            'metal': 'Silver 925',
            'size': '16cm, 17cm, 18cm',
        },
        {
            'title': 'Кольцо "Рубиновый закат"',
            'slug': 'ruby-sunset-ring',
            'category': 'rings',
            'brand': 'Marais',
            'price': 210000.00,
            'description': 'Золотое кольцо с натуральным рубином.',
            'metal': 'Rose Gold 585',
            'size': '16.5, 17.0, 17.5',
        },
        {
            'title': 'Серьги "Жемчужная капля"',
            'slug': 'pearl-drop-earrings',
            'category': 'earrings',
            'brand': 'Tiffany & Co.',
            'price': 95000.00,
            'description': 'Классические серьги с культивированным жемчугом.',
            'metal': 'Gold 750',
            'size': '',
        },
    ]

    for p_data in products_data:
        product, created = Product.objects.update_or_create(
            slug=p_data['slug'],
            defaults={
                'title': p_data['title'],
                'category': categories[p_data['category']],
                'brand_ref': brands[p_data['brand']],
                'price': p_data['price'],
                'description': p_data['description'],
                'metal': p_data['metal'],
                'size': p_data['size'],
                'stock': 10
            }
        )
        if created:
            print(f"Created Product: {product.title}")
        else:
            print(f"Product exists: {product.title}")

    print("Population completed successfully.")

if __name__ == '__main__':
    populate()
