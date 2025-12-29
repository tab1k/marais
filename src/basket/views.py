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
        
        # 1. Personal Discount
        discount_percent = 0
        if request.user.is_authenticated:
            discount_percent = request.user.discount_percent
        
        discount_amount = int(total * discount_percent / 100)
        # Persist the applied percent for use in WhatsApp checkout to keep totals consistent
        request.session['discount_percent_applied'] = discount_percent
        
        # 2. Bonuses
        # User requested bonuses to be used (stored in session temporarily)
        bonuses_to_use = request.session.get('bonuses_to_use', 0)
        user_bonuses = 0
        if request.user.is_authenticated:
            user_bonuses = request.user.loyalty_points
            
            # Validation: cannot use more than own balance
            if bonuses_to_use > user_bonuses:
                bonuses_to_use = user_bonuses
                request.session['bonuses_to_use'] = bonuses_to_use
        else:
            bonuses_to_use = 0
            
        # Validation: cannot use more than total - discount
        subtotal_after_discount = total - discount_amount
        if bonuses_to_use > subtotal_after_discount:
            bonuses_to_use = int(subtotal_after_discount)
            request.session['bonuses_to_use'] = bonuses_to_use

        final_total = total - discount_amount - bonuses_to_use
        
        return render(request, 'catalog/cart.html', {
            'cart': cart,
            'items': items,
            'total': total,
            'discount_percent': discount_percent,
            'discount_amount': discount_amount,
            'user_bonuses': user_bonuses,
            'bonuses_to_use': bonuses_to_use,
            'final_total': final_total,
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

class ApplyBonusesView(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('basket:detail')
            
        try:
            bonuses = int(request.POST.get('bonuses', 0))
        except ValueError:
            bonuses = 0
            
        # Validation happens in CartDetailView, but we can do basic checks here
        if bonuses < 0:
            bonuses = 0
            
        request.session['bonuses_to_use'] = bonuses
        return redirect('basket:detail')
