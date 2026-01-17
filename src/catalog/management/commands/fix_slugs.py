from django.core.management.base import BaseCommand
from slugify import slugify
from catalog.models import Product, Category, Brand, Collection

class Command(BaseCommand):
    help = 'Regenerate slugs for all catalog items using python-slugify (transliteration)'

    def handle(self, *args, **options):
        self.stdout.write("Fixing slugs for Categories...")
        for obj in Category.objects.all():
            new_slug = slugify(obj.name)
            if obj.slug != new_slug:
                obj.slug = new_slug
                try:
                    obj.save()
                except Exception:
                    obj.slug = f"{new_slug}-{obj.id}"
                    obj.save()
        
        self.stdout.write("Fixing slugs for Brands...")
        for obj in Brand.objects.all():
            new_slug = slugify(obj.name)
            # Brand model has custom save logic that checks if not self.slug
            # We explicitly set it, so it should be fine, but let's be careful since we modified Brand.save in thought but not in file?
            # Actually Brand.save uses django.utils.text.slugify if slug is empty. We are providing a slug so it should override.
            if obj.slug != new_slug:
                obj.slug = new_slug
                try:
                    obj.save()
                except Exception:
                    obj.slug = f"{new_slug}-{obj.id}"
                    obj.save()

        self.stdout.write("Fixing slugs for Collections...")
        for obj in Collection.objects.all():
            new_slug = slugify(obj.name)
            if obj.slug != new_slug:
                obj.slug = new_slug
                try:
                    obj.save()
                except Exception:
                    obj.slug = f"{new_slug}-{obj.id}"
                    obj.save()

        self.stdout.write("Fixing slugs for Products...")
        products = Product.objects.all()
        count = products.count()
        for i, obj in enumerate(products):
            # Same logic as import_google_sheet
            base = f"{obj.title}-{obj.article}"
            new_slug = slugify(base)
            if obj.slug != new_slug:
                obj.slug = new_slug
                try:
                    obj.save()
                except Exception:
                    obj.slug = f"{new_slug}-{obj.id}"
                    obj.save()
            
            if i % 100 == 0:
                self.stdout.write(f"Processed {i}/{count} products...")
        
        self.stdout.write(self.style.SUCCESS('Successfully fixed all slugs.'))
