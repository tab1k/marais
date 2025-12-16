from django.shortcuts import redirect
from django.views import View
from django.conf import settings
from django.utils.http import urlencode
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
            total_price=0 # Will update after items
        )

        # Create Items and Message
        message_lines = ["Здравствуйте! Хочу оформить заказ:"]
        total_price = 0

        for cart_item in cart.items.select_related('product').all():
            cost = cart_item.product.price * cart_item.quantity
            total_price += cost
            
            # Create OrderItem
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price,
                size=cart_item.size
            )
            
            # Add to message
            size_str = f" (Размер: {cart_item.size})" if cart_item.size else ""
            line = f"- {cart_item.product.name}{size_str} x{cart_item.quantity} — {cost} ₸"
            message_lines.append(line)

        # Update Order Total
        order.total_price = total_price
        order.status = 'sent'
        order.save()

        # Add total to message
        message_lines.append(f"\nИтого: {total_price} ₸")
        
        # Clear Cart
        cart.items.all().delete() # Or cart.delete() if you want to remove the cart entirely

        # Redirect to WhatsApp
        message_text = "\n".join(message_lines)
        base_url = f"https://wa.me/{settings.WHATSAPP_NUMBER}"
        query_string = urlencode({'text': message_text})
        
        return redirect(f"{base_url}?{query_string}")

