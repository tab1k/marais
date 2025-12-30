import requests
import csv
import re
import json
from io import StringIO

SHEET_URL = "https://docs.google.com/spreadsheets/d/1KaysYxaB-0z897sifpycDDC68C1EFPqydp23QheD2lY/export?format=csv"

def convert_gdrive_link(url):
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
    if not price_str:
        return 0
    price_str = price_str.replace('\xa0', '').replace(' ', '')
    digits = re.findall(r'\d+', price_str)
    if digits:
        return float(''.join(digits))
    return 0

def clean_stock(stock_str):
    try:
        return int(stock_str)
    except (ValueError, TypeError):
        return 0

def extract():
    response = requests.get(SHEET_URL)
    response.encoding = 'utf-8'
    f = StringIO(response.text)
    rows = list(csv.reader(f))
    data_rows = rows[1:]

    products_agg = {}

    for row in data_rows:
        if not any(row) or len(row) < 13:
            continue
            
        category_name = row[0].strip()
        article = row[1].strip()
        brand_name = row[2].strip()
        
        if not article or not category_name:
            continue

        size = row[7].strip()
        stock = clean_stock(row[13].strip())
        
        if article not in products_agg:
            description = row[8].strip()
            title = description.split('\n')[0].strip()[:200]
            if not title:
                title = f"{category_name} {brand_name} {article}"

            products_agg[article] = {
                'category': category_name,
                'article': article,
                'brand': brand_name,
                'title': title,
                'main_photo': convert_gdrive_link(row[3].strip()),
                'extra_photos': [
                    convert_gdrive_link(row[4].strip()), 
                    convert_gdrive_link(row[5].strip()), 
                    convert_gdrive_link(row[6].strip())
                ],
                'sizes': set(),
                'description': description,
                'material': row[9].strip(),
                'coverage': row[10].strip(),
                'stones': row[11].strip(),
                'price': clean_price(row[12].strip()),
                'total_stock': 0
            }
        
        if size:
            products_agg[article]['sizes'].add(size)
        products_agg[article]['total_stock'] += stock

    # Convert sets to sorted lists for JSON
    final_list = []
    for art, data in products_agg.items():
        data['sizes'] = sorted(list(data['sizes']))
        final_list.append(data)

    with open('products.json', 'w', encoding='utf-8') as jf:
        json.dump(final_list, jf, ensure_ascii=False, indent=2)
    
    print(f"Successfully extracted {len(final_list)} products to products.json")

if __name__ == "__main__":
    extract()
