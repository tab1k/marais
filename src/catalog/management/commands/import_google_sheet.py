
import csv
import io
import requests
import re
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from catalog.models import Product, Category, Brand, ProductImage

class Command(BaseCommand):
    help = 'Imports products from Google Sheet'

    def handle(self, *args, **options):
        # CSV Export URL
        url = 'https://docs.google.com/spreadsheets/d/1KaysYxaB-0z897sifpycDDC68C1EFPqydp23QheD2lY/export?format=csv&gid=686330706'
        
        self.stdout.write(f'Downloading CSV from {url}...')
        response = requests.get(url)
        response.raise_for_status()
        
        # Decode content
        content = response.content.decode('utf-8')
        file = io.StringIO(content)
        
        reader = csv.reader(file)
        headers = next(reader)
        
        # Identify columns by index to handle duplicate headers
        # Expected headers: 
        # Категория, Артикул, Бренд, Фото (ссылка) x4, Размер, Описание, Материал, Покрытие, Камень, Цена, Количество
        
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
            
            # Find all image indices
            img_indices = [i for i, h in enumerate(headers) if h == 'Фото (ссылка)']
            
        except ValueError as e:
            self.stderr.write(self.style.ERROR(f'Missing column header: {e}'))
            return

        self.stdout.write(f'Found {len(img_indices)} image columns.')

        created_count = 0
        updated_count = 0

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
                # Strategy: Split description by newline. First line is title, rest is description.
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
                    category, _ = Category.objects.get_or_create(
                        name__iexact=category_name,
                        defaults={'name': category_name, 'slug': cat_slug}
                    )

                # Get/Create Brand
                brand = None
                if brand_name:
                    brand_slug = slugify(brand_name, allow_unicode=True) or brand_name.lower().replace(' ', '-')
                    brand, _ = Brand.objects.get_or_create(
                        name__iexact=brand_name,
                        defaults={'name': brand_name, 'slug': brand_slug}
                    )

                # Create/Update Product
                product, created = Product.objects.update_or_create(
                    article=article,
                    defaults={
                        'title': title,
                        'slug': slugify(title + '-' + article, allow_unicode=True)[:200], # Ensure unique slug approx
                        'description': description,
                        'category': category,
                        'brand_ref': brand,
                        'brand': brand_name,
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
                # Collect Image URLs
                image_urls = []
                for idx in img_indices:
                    if idx < len(row):
                        raw_url = row[idx].strip()
                        if raw_url:
                            # Convert Google Drive link to direct link
                            # Format: https://drive.google.com/file/d/ID/view... -> https://drive.google.com/uc?export=view&id=ID
                            match = re.search(r'/d/([a-zA-Z0-9_-]+)', raw_url)
                            if match:
                                file_id = match.group(1)
                                direct_url = f'https://drive.google.com/uc?export=view&id={file_id}'
                                image_urls.append(direct_url)
                            else:
                                image_urls.append(raw_url)
                
                # Assign Main Image
                if image_urls:
                    product.main_image_url = image_urls[0]
                    product.save()
                    
                    # Create Gallery Images (skip first as it's main)
                    # First, clear existing gallery images to avoid dupes on re-run? 
                    # Or update? Let's clear for cleaner sync.
                    product.images.all().delete()
                    
                    for i, url in enumerate(image_urls[1:]):
                        ProductImage.objects.create(
                            product=product,
                            image_url=url,
                            sort_order=i
                        )

                if created:
                    created_count += 1
                else:
                    updated_count += 1
                    
            except Exception as e:
                 self.stdout.write(self.style.ERROR(f'Error processing row {article}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Import finished. Created: {created_count}, Updated: {updated_count}'))
