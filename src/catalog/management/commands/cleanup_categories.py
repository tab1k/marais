from django.core.management.base import BaseCommand
from catalog.models import Category, Product

class Command(BaseCommand):
    help = 'Merge duplicate categories and fix naming'

    def handle(self, *args, **options):
        # Define correct category names (canonical forms)
        CANONICAL_CATEGORIES = {
            'Кольца': ['кольцо', 'кольца', 'Кольцо'],
            'Браслеты': ['браслет', 'браслеты', 'Браслет'],
            'Серьги': ['серьга', 'серьги', 'Серьга'],
            'Сертификаты': ['сертификат', 'сертификаты', 'Сертификат'],
            'Колье': ['колье'],
        }

        for canonical_name, variants in CANONICAL_CATEGORIES.items():
            self.stdout.write(f'Processing {canonical_name}...')
            
            # Find or create canonical category
            canonical_cat, created = Category.objects.get_or_create(
                name=canonical_name,
                defaults={'slug': canonical_name.lower()}
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Created canonical category: {canonical_name}'))
            
            # Find all variant categories (case-insensitive)
            for variant in variants:
                duplicates = Category.objects.filter(name__iexact=variant).exclude(id=canonical_cat.id)
                
                for dup in duplicates:
                    # Move all products from duplicate to canonical
                    product_count = dup.products.count()
                    if product_count > 0:
                        dup.products.all().update(category=canonical_cat)
                        self.stdout.write(f'  Moved {product_count} products from "{dup.name}" to "{canonical_name}"')
                    
                    # Delete duplicate
                    dup.delete()
                    self.stdout.write(self.style.WARNING(f'  Deleted duplicate: {dup.name}'))
        
        self.stdout.write(self.style.SUCCESS('Category cleanup complete!'))
