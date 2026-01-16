import os
import django
import shutil

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marais.settings.development')
django.setup()

from catalog.models import HomepageBlock, Brand, Product

def populate_blocks():
    print("Populating homepage blocks...")
    
    # Clear existing blocks to avoid duplicates during dev
    HomepageBlock.objects.all().delete()
    
    # 1. Create a Brand Block (Marais / Flouida style)
    try:
        brand_marais = Brand.objects.get(name='Marais')
        # Find a suitable product for the "Featured Product" on the right side
        featured_prod = Product.objects.filter(brand_ref=brand_marais).first()
        
        block1 = HomepageBlock.objects.create(
            block_type='brand',
            title='Коллекция Flouida',
            brand=brand_marais,
            featured_product=featured_prod,
            image='blocks/flouida.png', # Relative to MEDIA_ROOT
            sort_order=1,
            is_active=True
        )
        print(f"Created Brand Block: {block1}")
    except Brand.DoesNotExist:
        print("Brand 'Marais' not found. Skipping Brand Block.")

    # 2. Create a Banner Block (Mishes style)
    block2 = HomepageBlock.objects.create(
        block_type='banner',
        title='Мишес',
        subtitle='КОЛЛЕКЦИЯ FLOUIDA',
        image='blocks/mishes.jpg',
        link_url='/catalog/',
        sort_order=2,
        is_active=True
    )
    print(f"Created Banner Block: {block2}")
    
    print("Homepage blocks populated.")

if __name__ == '__main__':
    populate_blocks()
