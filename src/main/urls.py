from . import views
from django.urls import path

urlpatterns = [
    path('', views.GeneralPageView.as_view(), name='general'),
    path('brand/', views.BrandPageView.as_view(), name='brand'),
    path('brand/<slug:slug>/', views.BrandDetailView.as_view(), name='brand_detail'),
    path('project/', views.ProjectPageView.as_view(), name='project'),
    path('api/subscribe/', views.NewsletterSubscribeView.as_view(), name='subscribe'),
]
