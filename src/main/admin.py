from django.contrib import admin
from .models import NewsletterSubscriber, TopBanner

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('email',)
    readonly_fields = ('created_at',)

@admin.register(TopBanner)
class TopBannerAdmin(admin.ModelAdmin):
    list_display = ('text', 'link', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('text',)
