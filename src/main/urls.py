from . import views
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('', views.GeneralPageView.as_view(), name='general'),
    path('brand/', views.BrandPageView.as_view(), name='brand'),
    path('brand/<slug:slug>/', views.BrandDetailView.as_view(), name='brand_detail'),
    path('project/', views.ProjectPageView.as_view(), name='project'),
    path('api/subscribe/', views.NewsletterSubscribeView.as_view(), name='subscribe'),
    path('privacy-policy/', TemplateView.as_view(template_name='main/privacy_policy.html'), name='privacy_policy'),
    path('public-offer/', TemplateView.as_view(template_name='main/public_offer.html'), name='public_offer'),
    path('payment-info/', TemplateView.as_view(template_name='main/payment_info.html'), name='payment_info'),
]
