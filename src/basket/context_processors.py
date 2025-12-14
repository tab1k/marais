from .models import Cart

def cart_processor(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    else:
        session_key = request.session.session_key
        if not session_key:
            return {'cart_total_quantity': 0}
        cart = Cart.objects.filter(session_key=session_key).first()
    
    if cart:
        return {'cart_total_quantity': cart.total_quantity}
    return {'cart_total_quantity': 0}
