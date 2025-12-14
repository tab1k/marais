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
            
        metals = request.GET.getlist('metal')
        if metals:
             clean_metals = [m for m in metals if m and m != 'None']
             if clean_metals:
                # Use Q objects if we need partially matching, but __in is better for checkboxes
                # However, if DB has "Gold 585" and we filter "Gold", __in won't match.
                # But checkboxes imply exact options. Let's assume exact match for now.
                products = products.filter(metal__in=clean_metals)

        coverages = request.GET.getlist('coverage')
        if coverages:
             clean_coverages = [c for c in coverages if c and c != 'None']
             if clean_coverages:
                products = products.filter(coverage__in=clean_coverages)

        stones_list = request.GET.getlist('stones')
        if stones_list:
             clean_stones = [s for s in stones_list if s and s != 'None']
             if clean_stones:
                products = products.filter(stones__in=clean_stones)
             
        colors = request.GET.getlist('color')
        if colors:
             clean_colors = [c for c in colors if c and c != 'None']
             if clean_colors:
                products = products.filter(color__in=clean_colors)

        sizes = request.GET.getlist('size')
        if sizes:
             clean_sizes = [s for s in sizes if s and s != 'None']
             if clean_sizes:
                products = products.filter(size__in=clean_sizes)
        
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
            'selected_metals': metals,
            'selected_coverages': coverages,
            'selected_stones': stones_list,
            'selected_colors': colors,
            'selected_sizes': sizes,
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
            results.append({
                'title': p.title,
                'slug': p.slug,
                'price': str(int(p.price)),
                'image': p.main_image.url if p.main_image else None,
                'brand': p.brand_ref.name if p.brand_ref else None
            })
        return JsonResponse({'results': results})
