import csv
import io
import requests
import re
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from catalog.models import Product, Category, Brand, ProductImage, Collection

class Command(BaseCommand):
    help = 'Imports products from Google Sheet'

    def handle(self, *args, **options):
        # New CSV Export URL
        url = 'https://docs.google.com/spreadsheets/d/1eN2uHHQvhF3zelpx7U5xB__XevHlj04lzfSkWhXVB6w/export?format=csv&gid=0'
        
        self.stdout.write('Clearing existing products...')
        # Clear all existing products. Images will be deleted via cascade if set up, 
        # but manual cleanup of ProductImage is good if Relation is different. 
        # Django's ForeignKey(on_delete=models.CASCADE) on ProductImage will handle it.
        Product.objects.all().delete()
        self.stdout.write('Existing products cleared.')

        self.stdout.write(f'Downloading CSV from {url}...')
        response = requests.get(url)
        response.raise_for_status()
        
        # Decode content
        content = response.content.decode('utf-8')
        file = io.StringIO(content)
        
        reader = csv.reader(file)
        headers = next(reader)
        
        # Expected headers: 
        # Категория, Артикул, Бренд, Фото (ссылка)..., Размер, Описание, Материал, Покрытие, Камень, Цена, Количество, Коллекции
        
        # Mapping indices
        try:
            cat_idx = headers.index('Категория')
            art_idx = headers.index('Артикул')
            brand_idx = headers.index('Бренд')
            size_idx = headers.index('Размер')
            desc_idx = headers.index('Описание')
            mat_idx = headers.index('Материал')
            cov_idx = headers.index('Покрытие')
            stone_idx = headers.index('Камень')
            price_idx = headers.index('Цена')
            qty_idx = headers.index('Количество')
            
            # Optional Collection column
            if 'Коллекции' in headers:
                col_idx = headers.index('Коллекции')
            else:
                col_idx = -1
            
            # Find all image indices by partial match or exact list
            # The new sheet has "Фото (ссылка)", "Фото (ссылка) 2", etc.
            img_indices = [i for i, h in enumerate(headers) if 'Фото (ссылка)' in h]
            
        except ValueError as e:
            self.stderr.write(self.style.ERROR(f'Missing column header: {e}'))
            return

        self.stdout.write(f'Found {len(img_indices)} image columns.')

        created_count = 0
        
        for row in reader:
            if not row or not any(row): continue
            
            try:
                # Extract basic data
                category_name = row[cat_idx].strip()
                article = row[art_idx].strip()
                brand_name = row[brand_idx].strip()
                size = row[size_idx].strip()
                raw_desc = row[desc_idx].strip()
                material = row[mat_idx].strip()
                coverage = row[cov_idx].strip()
                stones = row[stone_idx].strip()
                price_str = row[price_idx].strip()
                qty_str = row[qty_idx].strip()
                collection_name = row[col_idx].strip() if col_idx != -1 and col_idx < len(row) else ""
                
                if not article:
                    self.stdout.write(self.style.WARNING(f'Skipping row without article: {row}'))
                    continue

                # Parse Price
                try:
                    # Remove spaces, non-breaking spaces
                    clean_price = re.sub(r'\D', '', price_str)
                    price = int(clean_price) if clean_price else 0
                except ValueError:
                    price = 0
                
                # Parse Stock
                try:
                    stock = int(re.sub(r'\D', '', qty_str)) if qty_str else 0
                except ValueError:
                    stock = 0

                # Extract Title and Description
                lines = raw_desc.split('\n')
                if lines:
                    title = lines[0].strip()
                    description = "\n".join(lines[1:]).strip()
                else:
                    title = article 
                    description = ""
                
                if not title:
                    title = article

                # Get/Create Category
                category = None
                if category_name:
                    cat_slug = slugify(category_name, allow_unicode=True) or category_name.lower().replace(' ', '-')
                    # Use filter().first() to handle potential duplicates (case-insensitive)
                    existing_cats = Category.objects.filter(name__iexact=category_name)
                    if existing_cats.exists():
                        category = existing_cats.first()
                    else:
                        category = Category.objects.create(name=category_name, slug=cat_slug)

                # Get/Create Brand
                brand = None
                if brand_name:
                    brand_slug = slugify(brand_name, allow_unicode=True) or brand_name.lower().replace(' ', '-')
                    existing_brands = Brand.objects.filter(name__iexact=brand_name)
                    if existing_brands.exists():
                        brand = existing_brands.first()
                    else:
                        brand = Brand.objects.create(name=brand_name, slug=brand_slug)

                # Get/Create Collection
                collection = None
                if collection_name:
                    col_slug = slugify(collection_name, allow_unicode=True) or collection_name.lower().replace(' ', '-')
                    existing_cols = Collection.objects.filter(name__iexact=collection_name)
                    if existing_cols.exists():
                        collection = existing_cols.first()
                    else:
                        collection = Collection.objects.create(name=collection_name, slug=col_slug)

                # Create Product (since we deleted all, we just create)
                # But to be safe against duplicates in the CSV itself, we use update_or_create logic or get_or_create
                # Since article should be unique-ish, let's use it as lookup
                
                product, created = Product.objects.update_or_create(
                    article=article,
                    defaults={
                        'title': title,
                        'slug': slugify(title + '-' + article, allow_unicode=True)[:200], 
                        'description': description,
                        'category': category,
                        'brand_ref': brand,
                        'brand': brand_name,
                        'collection': collection,
                        'size': size,
                        'material': material,
                        'coverage': coverage,
                        'stones': stones,
                        'price': price,
                        'stock': stock,
                        'currency': '₸',
                        'is_active': True
                    }
                )
                
                # Handle Images
                image_urls = []
                for idx in img_indices:
                    if idx < len(row):
                        raw_url = row[idx].strip()
                        if raw_url:
                            # Convert Google Drive link
                            # Convert Google Drive link
                            # Handle /d/ID/ and open?id=ID
                            file_id = None
                            match_d = re.search(r'/d/([a-zA-Z0-9_-]+)', raw_url)
                            match_id = re.search(r'id=([a-zA-Z0-9_-]+)', raw_url)
                            
                            if match_d:
                                file_id = match_d.group(1)
                            elif match_id:
                                file_id = match_id.group(1)
                                
                            if file_id:
                                # Use lh3.googleusercontent.com for direct image access (avoids cookies/auth issues)
                                direct_url = f'https://lh3.googleusercontent.com/d/{file_id}'
                                image_urls.append(direct_url)
                            else:
                                image_urls.append(raw_url)
                
                if image_urls:
                    product.main_image_url = image_urls[0]
                    product.save()
                    
                    # Clear existing images if we updated an existing product (dup in csv)
                    product.images.all().delete()
                    
                    for i, url in enumerate(image_urls[1:]):
                        ProductImage.objects.create(
                            product=product,
                            image_url=url,
                            sort_order=i
                        )

                created_count += 1
                    
            except Exception as e:
                 self.stdout.write(self.style.ERROR(f'Error processing row {article}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Import finished. Processed/Created: {created_count} products.'))
