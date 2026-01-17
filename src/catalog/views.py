from django.shortcuts import render
from django.views import View

from basket.models import Order

from catalog.models import Product, Category, Brand, Collection

from django.core.paginator import Paginator

class CatalogView(View):
    def get(self, request):
        products = Product.objects.filter(is_active=True).order_by('-created_at')
        categories = Category.objects.all()
        brands = Brand.objects.filter(is_active=True)

        # Filters
        # Filters
        category_slugs = request.GET.getlist('category')
        clean_cats = []
        if category_slugs:
            # Handle 'None' or empty strings if any
            clean_cats = [c for c in category_slugs if c and c != 'None']
            if clean_cats:
                products = products.filter(category__slug__in=clean_cats)
        
        brand_names = request.GET.getlist('brand')
        if brand_names:
            clean_brands = [b for b in brand_names if b and b != 'None']
            if clean_brands:
                products = products.filter(brand_ref__name__in=clean_brands)

        collections = request.GET.getlist('collection')
        if collections:
            clean_collections = [c for c in collections if c and c != 'None']
            if clean_collections:
                # Filter by collection slug (or name, but slug is safer for URLs)
                # Model has 'slug' field. Let's assume URL param uses slug.
                products = products.filter(collection__slug__in=clean_collections)
        
        # Gender Filter
        genders = request.GET.getlist('gender')
        if genders:
            clean_genders = [g for g in genders if g and g != 'None']
            if clean_genders:
                products = products.filter(gender__in=clean_genders)

        # Removed Metal, Coverage, Stones, Color filters as requested

        available_sizes = set()
        
        # New filters collections
        available_metals = set()
        available_materials = set()
        available_stones = set()
        available_coverages = set()
        available_colors = set()

        # Collect available values from ACTIVE products (before filtering by attributes, but after categories/brands if desired)
        # However, typically we want facets to reflect current results or all possibilities.
        # Let's collect from 'products' which is currently filtered by Category and Brand.
        
        # Efficiently get distinct non-empty values
        # Note: We iterate once or use distinct() queries. For small DB iteration is fine, for large use individual queries.
        # Given this is likely not huge yet:
        
        for p in products:
             # Size
            if p.size:
                for s in p.size.split(','):
                    s_clean = s.strip()
                    if s_clean: available_sizes.add(s_clean)
            
            # Other text fields (exact match)
            if p.metal: available_metals.add(p.metal)
            if p.material: available_materials.add(p.material)
            if p.stones: available_stones.add(p.stones)
            if p.coverage: available_coverages.add(p.coverage)
            if p.color: available_colors.add(p.color)

        available_sizes = sorted(list(available_sizes))
        available_metals = sorted(list(available_metals))
        available_materials = sorted(list(available_materials))
        available_stones = sorted(list(available_stones))
        available_coverages = sorted(list(available_coverages))
        available_colors = sorted(list(available_colors))
            
        # --- Apply Filters ---

        # Size
        sizes = request.GET.getlist('size')
        if sizes:
             clean_sizes = [s for s in sizes if s and s != 'None']
             if clean_sizes:
                from django.db.models import Q
                q_objs = Q()
                for s in clean_sizes:
                    q_objs |= Q(size__icontains=s)
                products = products.filter(q_objs)

        # Metal
        metals = request.GET.getlist('metal')
        if metals:
            clean_metals = [v for v in metals if v and v != 'None']
            if clean_metals:
                products = products.filter(metal__in=clean_metals)

        # Material
        materials = request.GET.getlist('material')
        if materials:
            clean_vals = [v for v in materials if v and v != 'None']
            if clean_vals:
                products = products.filter(material__in=clean_vals)

        # Stones
        stones = request.GET.getlist('stones')
        if stones:
            clean_vals = [v for v in stones if v and v != 'None']
            if clean_vals:
                products = products.filter(stones__in=clean_vals)

        # Coverage
        coverage = request.GET.getlist('coverage')
        if coverage:
             clean_vals = [v for v in coverage if v and v != 'None']
             if clean_vals:
                products = products.filter(coverage__in=clean_vals)

        # Color
        colors = request.GET.getlist('color')
        if colors:
             clean_vals = [v for v in colors if v and v != 'None']
             if clean_vals:
                products = products.filter(color__in=clean_vals)

        # Price Range
        # Calculate min and max prices from all available products (before price filtering)
        price_min = None
        price_max = None
        if products.exists():
            from django.db.models import Min, Max
            price_range = products.aggregate(Min('price'), Max('price'))
            price_min = int(price_range['price__min'] or 0)
            price_max = int(price_range['price__max'] or 0)
        
        # Apply price filter if provided
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        
        if min_price:
            try:
                products = products.filter(price__gte=float(min_price))
            except ValueError:
                pass
        
        if max_price:
            try:
                products = products.filter(price__lte=float(max_price))
            except ValueError:
                pass

        # Pagination
        paginator = Paginator(products, 12) # 12 items per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'catalog/general.html', {
            'products': page_obj, 
            'page_obj': page_obj, 
            'categories': categories,
            'brands': brands,
            'selected_categories': clean_cats,
            'selected_brands': brand_names,
            'selected_collections': collections,
            'selected_genders': genders,
            'selected_sizes': sizes,
            'selected_metals': metals,
            'selected_materials': materials,
            'selected_stones': stones,
            'selected_coverage': coverage,
            'selected_colors': colors,
            
            'available_sizes': available_sizes,
            'available_metals': available_metals,
            'available_materials': available_materials,
            'available_stones': available_stones,
            'available_coverages': available_coverages,
            'available_colors': available_colors,
            
            'price_min': price_min,
            'price_max': price_max,
            'selected_min_price': min_price,
            'selected_max_price': max_price,
        })


from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

class ProductDetailView(View):
    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug, is_active=True)
        # Suggest related products (same category, exclude current)
        related_products = Product.objects.filter(category=product.category, is_active=True).exclude(id=product.id)[:15]
        
        # Complementary products (different category, for "Complete the Look")
        complementary_products = Product.objects.filter(is_active=True).exclude(category=product.category).exclude(id=product.id)[:15]
        
        sizes_list = []
        if product.size:
             sizes_list = [s.strip() for s in product.size.split(',') if s.strip() and s.strip() != '0']

        gallery_images = []
        if product.get_main_image_url:
            gallery_images.append(product.get_main_image_url)
        for img in product.images.all():
            if img.get_image_url and img.get_image_url not in gallery_images:
                gallery_images.append(img.get_image_url)

        referer = request.META.get('HTTP_REFERER', '')
        back_url = None
        if url_has_allowed_host_and_scheme(referer, allowed_hosts={request.get_host()}):
            back_url = referer

        return render(request, 'catalog/detail.html', {
            'product': product,
            'related_products': related_products,
            'complementary_products': complementary_products,
            'sizes_list': sizes_list,
            'back_url': back_url,
            'catalog_home_url': reverse('catalog:home'),
            'gallery_images': gallery_images,
        })





class ProfileView(View):
    def get(self, request):
        orders = []
        orders_total = 0
        if request.user.is_authenticated:
            qs = Order.objects.filter(user=request.user).prefetch_related('items__product').order_by('-created_at')
        else:
            # For guests, show orders from current session
            session_key = request.session.session_key
            if session_key:
                qs = Order.objects.filter(session_key=session_key, user__isnull=True).prefetch_related('items__product').order_by('-created_at')
            else:
                qs = Order.objects.none()

        orders_total = qs.count()
        orders = list(qs) # Show all orders
        
        # Get recommended products (random active products)
        recommended_products = Product.objects.filter(is_active=True).order_by('?')[:4]

        return render(request, 'catalog/profile.html', {
            'orders': orders,
            'orders_total': orders_total,
            'recommended_products': recommended_products,
        })


from django.http import JsonResponse

class SearchSuggestionsView(View):
    def get(self, request):
        query = request.GET.get('q', '').strip()
        results = []
        if query:
            from django.db.models import Q
            products = Product.objects.filter(
                Q(title__icontains=query) | Q(brand_ref__name__icontains=query),
                is_active=True
            ).select_related('brand_ref')[:5]
        else:
            # Show random suggestions if no query
            products = Product.objects.filter(is_active=True).order_by('?')[:5]

        for p in products:
            image_url = None
            is_placeholder = False
            
            if p.main_image:
                image_url = p.main_image.url
            elif p.brand_ref and p.brand_ref.logo:
                image_url = p.brand_ref.logo.url
                is_placeholder = True
            else:
                image_url = '/static/images/zaglushka.png'
                is_placeholder = True
                
            results.append({
                'title': p.title,
                'slug': p.slug,
                'price': str(int(p.price)),
                'image': image_url,
                'is_placeholder': is_placeholder,
                'brand': p.brand_ref.name if p.brand_ref else None
            })
        return JsonResponse({'results': results})
