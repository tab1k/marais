from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from catalog.models import Product
from .models import Cart, CartItem

def _get_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.save()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key, user=None)
    return cart

class CartDetailView(View):
    def get(self, request):
        cart = _get_cart(request)
        items = cart.items.select_related('product').all()
        total = sum(item.price * item.quantity for item in items)
        
        return render(request, 'catalog/cart.html', {
            'cart': cart,
            'items': items,
            'total': total
        })

class AddToCartView(View):
    def post(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        cart = _get_cart(request)
        size = request.POST.get('size')
        
        item, created = CartItem.objects.get_or_create(cart=cart, product=product, size=size)
        if not created:
            item.quantity += 1
            item.price = product.price # update price if changed
            item.save()
        else:
             item.price = product.price
             item.save()
             
        return redirect(request.META.get('HTTP_REFERER', 'catalog:home'))

class RemoveFromCartView(View):
    def post(self, request, pk):
        cart = _get_cart(request)
        item = get_object_or_404(CartItem, pk=pk, cart=cart)
        item.delete()
        return redirect('basket:detail')
        
class UpdateCartItemView(View):
    def post(self, request, pk):
        cart = _get_cart(request)
        item = get_object_or_404(CartItem, pk=pk, cart=cart)
        action = request.POST.get('action')
        
        if action == 'increment':
            item.quantity += 1
            item.save()
        elif action == 'decrement':
            if item.quantity > 1:
                item.quantity -= 1
                item.save()
            else:
                item.delete()
        return redirect('basket:detail')
