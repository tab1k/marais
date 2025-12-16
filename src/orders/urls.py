from django.urls import path
from .views import WhatsAppCheckoutView

app_name = 'orders'

urlpatterns = [
    path('checkout/', WhatsAppCheckoutView.as_view(), name='checkout'),
]
