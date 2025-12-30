from .models import TopBanner
from catalog.models import SiteSettings, Brand

def top_banner(request):
    banners = TopBanner.objects.filter(is_active=True)
    return {'top_banners': banners}

def site_settings(request):
    try:
        settings = SiteSettings.load()
    except:
        settings = None
    return {'site_settings': settings}

def all_brands(request):
    from django.db.models import Count
    brands = Brand.objects.annotate(product_count=Count('products')).filter(is_active=True, product_count__gt=0).order_by('sort_order', 'name')
    return {'all_brands': brands}

def all_collections(request):
    from catalog.models import Collection
    from django.db.models import Count
    # Display collections that have at least one product? Or all? User didn't specify, but similar to brands is safer.
    # But usually collections are curated, so maybe show all. Let's filter by having products to avoid empty pages.
    collections = Collection.objects.annotate(product_count=Count('products')).filter(product_count__gt=0).order_by('name')
    return {'all_collections': collections}
