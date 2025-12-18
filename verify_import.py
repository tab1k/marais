
import json
import os
import django
from collections import Counter

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marais.settings')
django.setup()

from catalog.models import Product, Brand

JSON_PATH = '/Users/tab1k/.gemini/antigravity/brain/c76df8dd-387e-4011-8b91-ff89f69522e0/products_data.json'

def verify_import():
    # 1. Load JSON Data
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    json_counts = Counter(item['brand'] for item in data)
    json_cat_counts = Counter(item['category'].strip().capitalize() for item in data if item['category'])
    
    print(f"Total in JSON: {len(data)}")
    print("\nJSON Counts per Brand:")
    for brand, count in json_counts.items():
        print(f"  {brand}: {count}")

    print("\nJSON Counts per Category:")
    for cat, count in json_cat_counts.items():
        print(f"  {cat}: {count}")

    # 2. Check Database
    db_counts = Counter()
    db_cat_counts = Counter()
    all_products = Product.objects.all()
    for p in all_products:
        # Use brand_ref if available, else brand char field
        b_name = p.brand_ref.name if p.brand_ref else p.brand
        db_counts[b_name] += 1
        c_name = p.category.name if p.category else "No Category"
        db_cat_counts[c_name] += 1
    
    print(f"\nTotal in DB: {all_products.count()}")
    print("\nDB Counts per Brand:")
    for brand, count in db_counts.items():
        print(f"  {brand}: {count}")

    print("\nDB Counts per Category:")
    for cat, count in db_cat_counts.items():
        print(f"  {cat}: {count}")

    # 3. Mismatches
    print("\n--- Comparison ---")
    all_brands = set(json_counts.keys()) | set(db_counts.keys())
    for brand in sorted(all_brands):
        j = json_counts.get(brand, 0)
        d = db_counts.get(brand, 0)
        if j != d:
            print(f"MISMATCH for {brand}: JSON={j}, DB={d}")
        else:
             print(f"OK for {brand}: {d}")

if __name__ == "__main__":
    verify_import()
