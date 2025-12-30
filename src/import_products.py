import os
import django
import requests
import csv
import re
from django.utils.text import slugify
from io import StringIO

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marais.settings')
django.setup()

from catalog.models import Category, Brand, Product, ProductImage

SHEET_URL = "https://docs.google.com/spreadsheets/d/1KaysYxaB-0z897sifpycDDC68C1EFPqydp23QheD2lY/export?format=csv"

def convert_gdrive_link(url):
    """Converts a Google Drive sharing link to a direct download link."""
    if not url or 'drive.google.com' not in url:
        return url
    
    # Extract file ID
    match = re.search(r'/d/([^/]+)', url)
    if match:
        file_id = match.group(1)
        return f"https://drive.google.com/uc?id={file_id}"
    
    match = re.search(r'id=([^&]+)', url)
    if match:
        file_id = match.group(1)
        return f"https://drive.google.com/uc?id={file_id}"
        
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
    """Transliteration and slugify for Russian text."""
    trans = str.maketrans("абвгдеёжзийклмнопрстуфхцчшщъыьэюя", "abvgdeejziyklmnoprstufhzcss-y-eua")
    slug = text.lower().translate(trans)
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    if not slug:
        import hashlib
        slug = hashlib.md5(text.encode()).hexdigest()[:10]
    return slug[:200]

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
    
    data_rows = rows[1:] # Skip header
    print(f"Found {len(data_rows)} rows. Aggregating data...")

    # Dictionary to aggregate product data by article
    products_agg = {}

    for i, row in enumerate(data_rows):
        if not any(row) or len(row) < 13: # Skip empty or short rows
            continue
            
        try:
            category_name = row[0].strip()
            article = row[1].strip()
            brand_name = row[2].strip()
            
            if not article or not category_name:
                continue

            size = row[7].strip()
            stock = clean_stock(row[13].strip())
            
            if article not in products_agg:
                products_agg[article] = {
                    'category_name': category_name,
                    'brand_name': brand_name,
                    'photo1': convert_gdrive_link(row[3].strip()),
                    'photos_extra': [convert_gdrive_link(row[4].strip()), 
                                    convert_gdrive_link(row[5].strip()), 
                                    convert_gdrive_link(row[6].strip())],
                    'sizes': set(),
                    'description': row[8].strip(),
                    'material': row[9].strip(),
                    'coverage': row[10].strip(),
                    'stones': row[11].strip(),
                    'price': clean_price(row[12].strip()),
                    'stock': 0
                }
            
            if size:
                products_agg[article]['sizes'].add(size)
            products_agg[article]['stock'] += stock

        except Exception as e:
            print(f"Row {i+2}: Error parsing: {e}")

    print(f"Importing {len(products_agg)} unique products...")

    for article, data in products_agg.items():
        try:
            # 1. Get/Create Category
            cat_name_cap = data['category_name'].capitalize()
            category, _ = Category.objects.get_or_create(
                name=cat_name_cap,
                defaults={'slug': get_slug(data['category_name'])}
            )

            # 2. Get/Create Brand
            brand_obj, _ = Brand.objects.get_or_create(
                name=data['brand_name'],
                defaults={'slug': get_slug(data['brand_name'])}
            )

            # 3. Create Title from description first line
            title = data['description'].split('\n')[0].strip()[:200]
            if not title:
                title = f"{data['category_name']} {data['brand_name']} {article}"

            # 4. Generate Product Slug
            prod_slug_base = f"{title}-{article}"
            prod_slug = slugify(prod_slug_base)
            if not prod_slug:
                prod_slug = get_slug(prod_slug_base)

            # 5. Prepare size string
            sizes_str = ", ".join(sorted(list(data['sizes'])))

            # 6. Create/Update Product
            product, created = Product.objects.update_or_create(
                article=article,
                defaults={
                    'category': category,
                    'brand_ref': brand_obj,
                    'brand': data['brand_name'],
                    'title': title,
                    'slug': prod_slug,
                    'description': data['description'],
                    'price': data['price'],
                    'material': data['material'],
                    'coverage': data['coverage'],
                    'stones': data['stones'],
                    'size': sizes_str,
                    'stock': data['stock'],
                    'main_image_url': data['photo1'],
                    'is_active': True
                }
            )
            
            verb = "Created" if created else "Updated"
            print(f"{verb} Product: {title} ({article}) - Sizes: {sizes_str}, Stock: {data['stock']}")

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
