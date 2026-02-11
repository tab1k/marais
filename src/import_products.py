import os
import django
import requests
import csv
import re
from slugify import slugify  # transliterates Cyrillic to ASCII
from io import StringIO

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marais.settings.development')
django.setup()

from catalog.models import Category, Brand, Collection, Product, ProductImage

SHEET_URL = "https://docs.google.com/spreadsheets/d/1eN2uHHQvhF3zelpx7U5xB__XevHlj04lzfSkWhXVB6w/export?format=csv&gid=0"

def convert_gdrive_link(url):
    """Converts a Google Drive sharing link to a direct download link."""
    if not url or 'drive.google.com' not in url:
        return url
    
    # Extract file ID
    match = re.search(r'/d/([^/]+)', url)
    if match:
        file_id = match.group(1)
        return f"https://lh3.googleusercontent.com/d/{file_id}"
    
    match = re.search(r'id=([^&]+)', url)
    if match:
        file_id = match.group(1)
        return f"https://lh3.googleusercontent.com/d/{file_id}"
        
    return url

def clean_price(price_str):
    """Removes spaces and non-digit characters from price string."""
    if not price_str:
        return 0
    # Remove non-breaking spaces and other whitespace
    price_str = price_str.replace('\xa0', '').replace(' ', '')
    # Extract only digits
    digits = re.findall(r'\d+', price_str)
    if digits:
        return float(''.join(digits))
    return 0

def clean_stock(stock_str):
    """Convert quantity to integer."""
    try:
        return int(stock_str)
    except (ValueError, TypeError):
        return 0

def get_slug(text):
    """Generate ASCII slug with transliteration and a stable fallback."""
    text = str(text or '').strip()
    slugified = slugify(text)
    if not slugified:
        import hashlib
        slugified = hashlib.md5(text.encode()).hexdigest()[:10]
    return slugified[:200]

def normalize_header(value):
    return re.sub(r'\s+', ' ', str(value or '').strip()).lower()

def header_index(headers, *names):
    normalized = {h: i for i, h in enumerate(headers)}
    for name in names:
        key = normalize_header(name)
        if key in normalized:
            return normalized[key]
    return None

def get_cell(row, idx):
    if idx is None or idx >= len(row):
        return ''
    return str(row[idx]).strip()

def map_gender(value):
    v = str(value or '').strip().lower()
    if not v:
        return None
    if 'муж' in v or v in ('m', 'male'):
        return 'male'
    if 'жен' in v or v in ('f', 'female'):
        return 'female'
    return None

def map_material_type(value):
    v = str(value or '').strip().lower()
    if not v:
        return None
    if 'ювелир' in v:
        return 'jewelry'
    if 'друг' in v:
        return 'other'
    return None

def map_stone_option(value):
    v = str(value or '').strip().lower()
    if not v:
        return None
    if 'без' in v:
        return 'without_stones'
    if 'с камн' in v or v.startswith('с '):
        return 'with_stones'
    return None

def split_list(value):
    if not value:
        return []
    parts = re.split(r'[,\n;]+', str(value))
    return [p.strip() for p in parts if p.strip()]

def import_data():
    print(f"Fetching data from {SHEET_URL}...")
    try:
        response = requests.get(SHEET_URL)
        response.raise_for_status()
        response.encoding = 'utf-8'
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    f = StringIO(response.text)
    rows = list(csv.reader(f))
    if not rows:
        print("Empty spreadsheet.")
        return

    headers_raw = rows[0]
    headers = [normalize_header(h) for h in headers_raw]

    cat_idx = header_index(headers, 'Категория')
    art_idx = header_index(headers, 'Артикул')
    brand_idx = header_index(headers, 'Бренд')
    size_idx = header_index(headers, 'Размер')
    size_note_idx = header_index(headers, 'Размер описание', 'Размер (описание)')
    title_idx = header_index(headers, 'Название', 'Наименование')
    desc_idx = header_index(headers, 'Описание', 'Description')
    material_idx = header_index(headers, 'Материал')
    material_type_idx = header_index(headers, 'Материал фильтр', 'Материал (фильтр)')
    coverage_idx = header_index(headers, 'Покрытие')
    stones_idx = header_index(headers, 'Камень', 'Камни')
    stone_option_idx = header_index(headers, 'Камень фильтр', 'Камни фильтр')
    price_idx = header_index(headers, 'Цена', 'Price')
    qty_idx = header_index(headers, 'Количество', 'Остаток', 'Кол-во')
    collection_idx = header_index(headers, 'Коллекции', 'Коллекция')
    gender_idx = header_index(headers, 'Пол', 'Gender')

    img_indices = [i for i, h in enumerate(headers) if 'фото' in h]

    if art_idx is None:
        print("Missing required column: Артикул")
        return

    data_rows = rows[1:] # Skip header
    print(f"Found {len(data_rows)} rows. Aggregating data...")

    # Dictionary to aggregate product data by article
    products_agg = {}

    for i, row in enumerate(data_rows):
        if not any(row): # Skip empty rows
            continue
            
        try:
            category_name = get_cell(row, cat_idx)
            article = get_cell(row, art_idx)
            brand_name = get_cell(row, brand_idx)
            
            if not article:
                continue

            size = get_cell(row, size_idx)
            size_note = get_cell(row, size_note_idx)
            title_raw = get_cell(row, title_idx)
            description = get_cell(row, desc_idx)
            material = get_cell(row, material_idx)
            material_type = map_material_type(get_cell(row, material_type_idx))
            coverage = get_cell(row, coverage_idx)
            stones = get_cell(row, stones_idx)
            stone_option = map_stone_option(get_cell(row, stone_option_idx))
            price = clean_price(get_cell(row, price_idx))
            stock = clean_stock(get_cell(row, qty_idx))
            collections_raw = get_cell(row, collection_idx)
            gender = map_gender(get_cell(row, gender_idx))

            image_urls = []
            for idx in img_indices:
                img_url = get_cell(row, idx)
                if img_url:
                    image_urls.append(convert_gdrive_link(img_url))
            
            if article not in products_agg:
                products_agg[article] = {
                    'category_name': category_name,
                    'brand_name': brand_name,
                    'title': title_raw,
                    'description': description,
                    'note': size_note,
                    'material': material,
                    'material_type': material_type,
                    'coverage': coverage,
                    'stones': stones,
                    'stone_option': stone_option,
                    'gender': gender,
                    'photo1': image_urls[0] if image_urls else '',
                    'photos_extra': image_urls[1:] if len(image_urls) > 1 else [],
                    'sizes': set(),
                    'size_stock': {},
                    'price': price,
                    'collections': set(split_list(collections_raw)),
                    'stock': 0
                }
            else:
                data = products_agg[article]
                if category_name and not data.get('category_name'):
                    data['category_name'] = category_name
                if brand_name and not data.get('brand_name'):
                    data['brand_name'] = brand_name
                if title_raw and not data.get('title'):
                    data['title'] = title_raw
                if description and not data.get('description'):
                    data['description'] = description
                if size_note and not data.get('note'):
                    data['note'] = size_note
                if material and not data.get('material'):
                    data['material'] = material
                if material_type and not data.get('material_type'):
                    data['material_type'] = material_type
                if coverage and not data.get('coverage'):
                    data['coverage'] = coverage
                if stones and not data.get('stones'):
                    data['stones'] = stones
                if stone_option and not data.get('stone_option'):
                    data['stone_option'] = stone_option
                if gender and not data.get('gender'):
                    data['gender'] = gender
                if price and not data.get('price'):
                    data['price'] = price
                if collections_raw:
                    data['collections'].update(split_list(collections_raw))
                if image_urls:
                    if not data.get('photo1'):
                        data['photo1'] = image_urls[0]
                    for extra in image_urls[1:]:
                        if extra and extra != data['photo1'] and extra not in data['photos_extra']:
                            data['photos_extra'].append(extra)
            
            if size:
                products_agg[article]['sizes'].add(size)
                products_agg[article]['size_stock'][size] = products_agg[article]['size_stock'].get(size, 0) + stock
            products_agg[article]['stock'] += stock

        except Exception as e:
            print(f"Row {i+2}: Error parsing: {e}")

    print(f"Importing {len(products_agg)} unique products...")

    for article, data in products_agg.items():
        try:
            # 1. Get/Create Category
            cat_name_raw = (data.get('category_name') or '').strip()
            cat_name_cap = cat_name_raw.capitalize() if cat_name_raw else ''
            category = None
            if cat_name_cap:
                existing_cat = Category.objects.filter(name__iexact=cat_name_cap).first()
                if existing_cat:
                    category = existing_cat
                else:
                    category = Category.objects.create(
                        name=cat_name_cap,
                        slug=get_slug(cat_name_cap)
                    )

            # 2. Get/Create Brand
            brand_obj = None
            brand_name = (data.get('brand_name') or '').strip()
            if brand_name:
                existing_brand = Brand.objects.filter(name__iexact=brand_name).first()
                if existing_brand:
                    brand_obj = existing_brand
                else:
                    brand_obj = Brand.objects.create(
                        name=brand_name,
                        slug=get_slug(brand_name)
                    )

            # 3. Create Title from description first line
            title = (data.get('title') or '').strip()
            if not title:
                title = (data.get('description') or '').split('\n')[0].strip()[:200]
            if not title:
                title = f"{cat_name_cap} {brand_name} {article}".strip()

            # 4. Generate Product Slug
            prod_slug_base = f"{title}-{article}"
            prod_slug = get_slug(prod_slug_base)

            # 5. Prepare size string
            sizes_str = ", ".join(sorted(list(data['sizes'])))
            size_stock_map = {k: v for k, v in (data.get('size_stock') or {}).items() if k}
            total_stock = sum(size_stock_map.values()) if size_stock_map else data['stock']

            # 6. Create/Update Product
            product, created = Product.objects.update_or_create(
                article=article,
                defaults={
                    'category': category,
                    'brand_ref': brand_obj,
                    'brand': brand_name,
                    'title': title,
                    'slug': prod_slug,
                    'description': data.get('description') or '',
                    'price': data.get('price') or 0,
                    'material': data.get('material') or '',
                    'material_type': data.get('material_type'),
                    'coverage': data.get('coverage') or '',
                    'stones': data.get('stones') or '',
                    'stone_option': data.get('stone_option'),
                    'gender': data.get('gender'),
                    'note': data.get('note') or '',
                    'size': sizes_str,
                    'size_stock': size_stock_map,
                    'stock': total_stock,
                    'main_image_url': data.get('photo1') or '',
                    'is_active': True
                }
            )

            collection_names = sorted(list(data.get('collections') or []))
            if collection_names:
                collection_objs = []
                for name in collection_names:
                    existing = Collection.objects.filter(name__iexact=name).first()
                    if existing:
                        collection_objs.append(existing)
                    else:
                        collection_objs.append(Collection.objects.create(name=name, slug=get_slug(name)))
                product.collections.set(collection_objs)
            else:
                product.collections.clear()
            
            verb = "Created" if created else "Updated"
            print(f"{verb} Product: {title} ({article}) - Sizes: {sizes_str}, Stock: {total_stock}")

            # 7. Handle additional images
            ProductImage.objects.filter(product=product).delete()
            for img_url in data['photos_extra']:
                if img_url:
                    ProductImage.objects.create(product=product, image_url=img_url)

        except Exception as e:
            print(f"Error importing article {article}: {e}")

    print("Import finished.")

if __name__ == "__main__":
    import_data()
