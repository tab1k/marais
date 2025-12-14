from django.urls import path
from .views import CatalogView, ProductDetailView, ProfileView, SearchSuggestionsView

app_name = 'catalog'

urlpatterns = [
	path('', CatalogView.as_view(), name='home'),
	path('detail/<slug:slug>/', ProductDetailView.as_view(), name='detail'),
    path('search/suggestions/', SearchSuggestionsView.as_view(), name='search_suggestions'),

	path('profile/', ProfileView.as_view(), name='profile'),
]
