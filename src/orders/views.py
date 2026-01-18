from decimal import Decimal

from django.conf import settings
from django.shortcuts import redirect
from django.utils.http import urlencode
from django.views import View

from basket.models import Cart
from .models import Order, OrderItem

class WhatsAppCheckoutView(View):
    def get(self, request):
        user = request.user if request.user.is_authenticated else None
        
        # Get cart
        if user:
            cart = Cart.objects.filter(user=user).first()
        else:
            session_key = request.session.session_key
            cart = Cart.objects.filter(session_key=session_key).first()

        if not cart or not cart.items.exists():
            return redirect('basket:detail')

        # Create Order
        order = Order.objects.create(
            user=user,
            session_key=request.session.session_key,
            total_price=0  # Will update after items
        )

        # Create Items and Message
        message_lines = ["Здравствуйте! Хочу оформить заказ:"]
        total_price = Decimal('0')

        for cart_item in cart.items.select_related('product').all():
            # Always use the cart item's stored price to mirror cart totals
            item_price = Decimal(cart_item.price)
            cost = item_price * cart_item.quantity
            total_price += cost
            
            # Create OrderItem
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=item_price,
                size=cart_item.size
            )

            # Decrease stock per size if tracked
            product_obj = cart_item.product
            if product_obj:
                size_stock_map = product_obj.size_stock_map
                if size_stock_map and cart_item.size:
                    current_qty = size_stock_map.get(cart_item.size, 0)
                    size_stock_map[cart_item.size] = max(current_qty - cart_item.quantity, 0)
                    product_obj.size_stock = size_stock_map
                    product_obj.stock = max(sum(size_stock_map.values()), 0)
                else:
                    product_obj.stock = max((product_obj.stock or 0) - cart_item.quantity, 0)
                product_obj.save()
            
            # Add to message
            size_str = f" (Размер: {cart_item.size})" if cart_item.size else ""
            line = f"- {cart_item.product.title}{size_str} x{cart_item.quantity} — {cost} ₸"
            message_lines.append(line)

        # --- Calculate Discounts and Bonuses ---
        # Try to reuse the same discount percent that was applied in cart
        discount_percent = int(request.session.get('discount_percent_applied', 0))
        effective_user = user or cart.user  # fallback to cart owner if session lost auth
        if discount_percent <= 0 and effective_user:
            # Use user-specific discount, or fallback baseline 15% if user exists but has 0
            discount_percent = effective_user.discount_percent or 15
        discount_amount = int(total_price * discount_percent / 100)
        
        # Bonuses
        bonuses_used = request.session.get('bonuses_to_use', 0)
        
        # Validate bonuses again (security check)
        if effective_user:
            if bonuses_used > effective_user.loyalty_points:
                bonuses_used = effective_user.loyalty_points
        else:
            bonuses_used = 0 # Anonymous users can't use bonuses

        subtotal_after_discount = total_price - Decimal(discount_amount)
        if bonuses_used > subtotal_after_discount:
            bonuses_used = int(subtotal_after_discount)
            
        final_total = total_price - Decimal(discount_amount) - Decimal(bonuses_used)
        if final_total < 0:
            final_total = Decimal('0')
        
        # --- Update Order ---
        order.total_price = total_price.quantize(Decimal('1.'))
        order.discount_amount = Decimal(discount_amount)
        order.bonuses_used = bonuses_used
        order.final_price = final_total
        order.status = 'sent'
        order.save()
        
        # --- Update User Balance ---
        if user and bonuses_used > 0:
            user.loyalty_points -= bonuses_used
            user.save()
            request.session['bonuses_to_use'] = 0 # Reset session

        # --- Add details to message ---
        if discount_amount > 0:
            message_lines.append(f"Скидка ({discount_percent}%): -{int(discount_amount)} ₸")
        if bonuses_used > 0:
            message_lines.append(f"Списано бонусов: -{bonuses_used} B")

        message_lines.append(f"\nИтого к оплате: {int(final_total)} ₸")
        message_lines.append("\nПожалуйста, подтвердите заказ.")
        
        # Clear Cart
        cart.items.all().delete() # Or cart.delete() if you want to remove the cart entirely

        # Redirect to WhatsApp
        message_text = "\n".join(message_lines)
        base_url = f"https://wa.me/{settings.WHATSAPP_NUMBER}"
        query_string = urlencode({'text': message_text})
        
        return redirect(f"{base_url}?{query_string}")
