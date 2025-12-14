import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marais.settings')
django.setup()

from catalog.models import Product

def assign_images():
    print("Assigning images to products...")
    
    # Map slugs to filenames in media/products/
    mapping = {
        'diamond-sparkle-ring': 'kolca.png',
        'golden-loop-earrings': 'sergi.png',
        'silver-chain-necklace': 'zolotoe_ozh.png', # using this as placeholder for silver too
        'charm-bracelet': 'braslet.png',
        'ruby-sunset-ring': 'kolca.png',
        'pearl-drop-earrings': 'sergi1.png',
        'cascade': 'cascade.png', # if exists
    }

    for slug, filename in mapping.items():
        try:
            product = Product.objects.get(slug=slug)
            # define path relative to MEDIA_ROOT
            product.main_image = f'products/{filename}'
            product.save()
            print(f"Updated {product.title} with image {filename}")
        except Product.DoesNotExist:
            print(f"Product with slug {slug} not found.")

    print("Image assignment completed.")

if __name__ == '__main__':
    assign_images()
