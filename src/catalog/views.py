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

        # Removed Metal, Coverage, Stones, Color filters as requested

        available_sizes = set()
        if category_slugs:
            # Get all sizes for products in the current filtered set (by category/brand)
            # We use a separate query or iterate the current queryset to find available sizes
            # optimization: use values_list on the current 'products' queryset
            # Note: 'products' at this point is filtered by category and brand
            raw_sizes = products.exclude(size='').values_list('size', flat=True)
            for s_str in raw_sizes:
                # Assuming size can be "16, 17" or just "16"
                for s in s_str.split(','):
                    s_clean = s.strip()
                    if s_clean:
                        available_sizes.add(s_clean)
            
        # Filter by selected sizes
        sizes = request.GET.getlist('size')
        if sizes:
             clean_sizes = [s for s in sizes if s and s != 'None']
             if clean_sizes:
                # Filter products that CONTAIN the selected size
                # Since size is a string "16, 17", we might need partial match for each selected size
                # OR logic: if product has ANY of the selected sizes
                from django.db.models import Q
                q_objs = Q()
                for s in clean_sizes:
                    q_objs |= Q(size__icontains=s)
                products = products.filter(q_objs)
        
        available_sizes = sorted(list(available_sizes))
        
        # Pagination
        paginator = Paginator(products, 12) # 12 items per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'catalog/general.html', {
            'products': page_obj, # This works for iteration
            'page_obj': page_obj, # This works for pagination controls
            'categories': categories,
            'brands': brands,
            'selected_categories': category_slugs,
            'selected_brands': brand_names,
            'selected_sizes': sizes,
            'available_sizes': available_sizes,
        })


from django.shortcuts import get_object_or_404

class ProductDetailView(View):
    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug, is_active=True)
        # Suggest related products (same category, exclude current)
        related_products = Product.objects.filter(category=product.category, is_active=True).exclude(id=product.id)[:4]
        
        # Complementary products (different category, for "Complete the Look")
        complementary_products = Product.objects.filter(is_active=True).exclude(category=product.category).exclude(id=product.id)[:4]
        
        sizes_list = []
        if product.size:
             sizes_list = [s.strip() for s in product.size.split(',') if s.strip()]

        return render(request, 'catalog/detail.html', {
            'product': product,
            'related_products': related_products,
            'complementary_products': complementary_products,
            'sizes_list': sizes_list,
        })





class ProfileView(View):
    def get(self, request):
        orders = []
        orders_total = 0
        if request.user.is_authenticated:
            qs = Order.objects.filter(user=request.user).prefetch_related('items__product').order_by('-created_at')
            orders_total = qs.count()
            orders = list(qs[:3])
        
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
            products = Product.objects.filter(title__icontains=query, is_active=True)[:5]
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
                image_url = '/static/images/logo.png'
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
