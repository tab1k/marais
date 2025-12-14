from django.urls import path
from .views import CartDetailView, AddToCartView, RemoveFromCartView, UpdateCartItemView

app_name = 'basket'

urlpatterns = [
	path('', CartDetailView.as_view(), name='detail'),
    path('add/<slug:slug>/', AddToCartView.as_view(), name='add'),
    path('remove/<int:pk>/', RemoveFromCartView.as_view(), name='remove'),
    path('update/<int:pk>/', UpdateCartItemView.as_view(), name='update'),
]

