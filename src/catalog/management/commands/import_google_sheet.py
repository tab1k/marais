import csv
import io
import requests
import re
from django.core.management.base import BaseCommand
# from django.utils.text import slugify # We use python-slugify now
from slugify import slugify
from catalog.models import Product, Category, Brand, ProductImage, Collection

class Command(BaseCommand):
    help = 'Imports products from Google Sheet'

    def handle(self, *args, **options):
        # New CSV Export URL
        url = 'https://docs.google.com/spreadsheets/d/1eN2uHHQvhF3zelpx7U5xB__XevHlj04lzfSkWhXVB6w/export?format=csv&gid=0'
        
        self.stdout.write('Clearing existing products, categories, brands, collections...')
        Product.objects.all().delete()
        Category.objects.all().delete()
        Brand.objects.all().delete()
        Collection.objects.all().delete()
        self.stdout.write('All catalog data cleared.')

        self.stdout.write(f'Downloading CSV from {url}...')
        response = requests.get(url)
        response.raise_for_status()
        
        # Decode content
        content = response.content.decode('utf-8')
        file = io.StringIO(content)
        
        reader = csv.reader(file)
        headers = next(reader)
        
        # Expected headers...
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
            
            if 'Коллекции' in headers:
                col_idx = headers.index('Коллекции')
            else:
                col_idx = -1

            if 'Пол' in headers:
                gender_idx = headers.index('Пол')
            elif 'Gender' in headers:
                gender_idx = headers.index('Gender')
            else:
                gender_idx = -1
            
            img_indices = [i for i, h in enumerate(headers) if 'Фото (ссылка)' in h]
            
        except ValueError as e:
            self.stderr.write(self.style.ERROR(f'Missing column header: {e}'))
            return

        self.stdout.write(f'Found {len(img_indices)} image columns.')

        created_count = 0
        
        # Normalization Map - expanded to catch all variants
        CATEGORY_MAP = {
            'кольцо': 'Кольца',
            'кольца': 'Кольца',
            'браслет': 'Браслеты',
            'браслеты': 'Браслеты',
            'серьга': 'Серьги',
            'серьги': 'Серьги',
            'сертификат': 'Сертификаты',
            'сертификаты': 'Сертификаты',
            'колье': 'Колье',
            # Keep other categories as-is
            '2в1': '2в1',
            'другое': 'Другое',
            'заколка': 'Заколка',
            'слейв': 'Слейв',
        }

        for row in reader:
            if not row or not any(row): continue
            
            try:
                # Extract basic data
                raw_cat = row[cat_idx].strip()
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
                gender_raw = row[gender_idx].strip() if gender_idx != -1 and gender_idx < len(row) else ""
                
                if not article:
                    self.stdout.write(self.style.WARNING(f'Skipping row without article: {row}'))
                    continue
                
                # Normalize Category Name
                category_name = raw_cat
                if raw_cat:
                    # Check lower case against map
                    normalized = CATEGORY_MAP.get(raw_cat.lower())
                    if normalized:
                        category_name = normalized
                    else:
                        # Capitalize first letter if not in map
                        category_name = raw_cat.capitalize()

                # Parse Price
                try:
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

                # Determine Gender
                gender = None
                if gender_raw:
                    gr = gender_raw.lower()
                    if 'муж' in gr or 'male' in gr:
                        gender = 'male'
                    elif 'жен' in gr or 'female' in gr:
                        gender = 'female'

                # Get/Create Category
                category = None
                if category_name:
                    # New slugify is transliterating by default
                    cat_slug = slugify(category_name)
                    # Use filter().first() to handle potential duplicates (case-insensitive)
                    existing_cats = Category.objects.filter(name__iexact=category_name)
                    if existing_cats.exists():
                        category = existing_cats.first()
                    else:
                        category = Category.objects.create(name=category_name, slug=cat_slug)

                # Get/Create Brand
                brand = None
                if brand_name:
                    brand_slug = slugify(brand_name)
                    existing_brands = Brand.objects.filter(name__iexact=brand_name)
                    if existing_brands.exists():
                        brand = existing_brands.first()
                    else:
                        brand = Brand.objects.create(name=brand_name, slug=brand_slug)

                # Get/Create Collections (comma-separated)
                collections = []
                if collection_name:
                    collection_names = [c.strip() for c in collection_name.split(',') if c.strip()]
                    for col_name in collection_names:
                        col_slug = slugify(col_name)
                        existing_cols = Collection.objects.filter(name__iexact=col_name)
                        if existing_cols.exists():
                            collection = existing_cols.first()
                        else:
                            collection = Collection.objects.create(name=col_name, slug=col_slug)
                        collections.append(collection)

                # Create Product (since we deleted all, we just create)
                # But to be safe against duplicates in the CSV itself, we use update_or_create logic or get_or_create
                # Since article should be unique-ish, let's use it as lookup
                
                product, created = Product.objects.update_or_create(
                    article=article,
                    defaults={
                        'title': title,
                        'slug': slugify(title + '-' + article), 
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
                        'gender': gender,
                        'is_active': True
                    }
                )

                if collections:
                    product.collections.set(collections)
                else:
                    product.collections.clear()
                
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
