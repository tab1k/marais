from .models import TopBanner
from catalog.models import SiteSettings

def top_banner(request):
    banners = TopBanner.objects.filter(is_active=True)
    return {'top_banners': banners}

def site_settings(request):
    try:
        settings = SiteSettings.load()
    except:
        settings = None
    return {'site_settings': settings}
