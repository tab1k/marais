from django.contrib import admin
from .models import NewsletterSubscriber

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('email',)
    readonly_fields = ('created_at',)
