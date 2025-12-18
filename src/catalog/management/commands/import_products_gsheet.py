
import json
import os
import requests
import time
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.core.files.base import ContentFile
from catalog.models import Product, Brand, Category, ProductImage
from django.db import transaction
import re

from django.conf import settings

class Command(BaseCommand):
    help = 'Import products from parsed JSON file'

    def handle(self, *args, **options):
        # json_path = '/Users/tab1k/.gemini/antigravity/brain/c76df8dd-387e-4011-8b91-ff89f69522e0/products_data.json'
        json_path = os.path.join(settings.BASE_DIR, 'catalog', 'fixtures', 'products_data.json')
        
        if not os.path.exists(json_path):
            self.stdout.write(self.style.ERROR(f'File not found: {json_path}'))
            return

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.stdout.write(f"Found {len(data)} products to import.")

        for item in data:
            try:
                self.import_product(item)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error importing {item.get('title')}: {e}"))

    def transliterate(self, text):
        ru = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
        }
        text = text.lower()
        result = []
        for char in text:
            if char in ru:
                result.append(ru[char])
            else:
                result.append(char)
        return ''.join(result)

    def myslugify(self, text):
        return slugify(self.transliterate(str(text)))

    def import_product(self, item):
        with transaction.atomic():
            # 1. Brand
            brand_name = item['brand'].strip()
            brand, _ = Brand.objects.get_or_create(name=brand_name)

            # 2. Category
            category_name = item['category'].strip().capitalize()
            if not category_name:
                category_name = "Другое"
            
            cat_slug = self.myslugify(category_name)
            if not cat_slug:
                 cat_slug = f"cat-{abs(hash(category_name))}"

            category, _ = Category.objects.get_or_create(
                name=category_name,
                defaults={'slug': cat_slug}
            )

            # 3. Product
            title = item['title']
            if not title:
                title = f"{category_name} {brand_name}"
            
            base_slug = self.myslugify(title)
            if not base_slug:
                 base_slug = f"product-{int(time.time())}"
            
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            price = item['price']
            
            product = Product.objects.create(
                category=category,
                brand_ref=brand,
                brand=brand.name, # Legacy char field
                title=title,
                slug=slug,
                description=item['description'],
                price=price,
                metal=item['metal'],
                material=item['material'],
                coverage=item['coverage'],
                stones=item['stones'],
                size=item['size'],
                is_active=True
            )

            # 4. Images
            images = item['images']
            if images:
                # Main image
                main_img_url = images[0]
                self.download_and_save_image(product, main_img_url, is_main=True)

                # Gallery images
                for i, img_url in enumerate(images[1:], start=1):
                    self.download_and_save_image(product, img_url, is_main=False, sort_order=i)

            self.stdout.write(self.style.SUCCESS(f"Imported: {product.title}"))

    def download_and_save_image(self, product, url, is_main=False, sort_order=0):
        # Convert Google Drive URL to direct link
        # Pattern: /file/d/VIDEO_ID/ or /file/d/VIDEO_ID
        # Actually usually /file/d/FILE_ID/view...
        file_id_match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
        if not file_id_match:
            self.stdout.write(self.style.WARNING(f"Could not extract ID from url: {url}"))
            return

        file_id = file_id_match.group(1)
        download_url = f'https://drive.google.com/uc?export=download&id={file_id}'

        try:
            # Add timeout
            response = requests.get(download_url, timeout=10)
            if response.status_code == 200:
                # Guess filename
                filename = f"{product.slug}_{'main' if is_main else sort_order}.jpg"
                
                # Check for Content-Disposition header for real filename? No, manual naming is safer.
                
                content_file = ContentFile(response.content)
                
                if is_main:
                    product.main_image.save(filename, content_file, save=True)
                else:
                    ProductImage.objects.create(
                        product=product,
                        image=ContentFile(response.content, name=filename),
                        sort_order=sort_order
                    )
            else:
                self.stdout.write(self.style.WARNING(f"Failed to download {url}: Status {response.status_code}"))

        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Error downloading {url}: {e}"))

