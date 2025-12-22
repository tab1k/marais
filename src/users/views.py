from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

class LoginView(View):
    template_name = 'users/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(reverse('catalog:profile'))
        return render(request, self.template_name, {'error': None})

    def post(self, request):
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        next_url = request.POST.get('next') or reverse('catalog:profile')

        UserModel = get_user_model()
        user_obj = UserModel.objects.filter(email=email).first()
        if not user_obj:
            return render(request, self.template_name, {'error': 'Пользователь не найден', 'email': email})

        user = authenticate(request, username=user_obj.username, password=password)
        if user:
            # Check for anonymous cart BEFORE login (session cycle)
            session_key = request.session.session_key
            anon_cart = None
            if session_key:
                from basket.models import Cart
                anon_cart = Cart.objects.filter(session_key=session_key, user__isnull=True).first()

            login(request, user)

            # Merge carts after login
            if anon_cart:
                user_cart, _ = Cart.objects.get_or_create(user=user)
                for item in anon_cart.items.all():
                    # Check if item exists in user_cart
                    existing_item = user_cart.items.filter(product=item.product, size=item.size).first()
                    if existing_item:
                        existing_item.quantity += item.quantity
                        existing_item.save()
                    else:
                        item.cart = user_cart
                        item.save()
                anon_cart.delete()

            # Attach anonymous orders to user
            from orders.models import Order
            Order.objects.filter(session_key=session_key, user__isnull=True).update(user=user)

            return redirect(next_url)

        return render(request, self.template_name, {'error': 'Неверный пароль', 'email': email})


class RegisterView(View):
    template_name = 'users/register.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(reverse('catalog:profile'))
        return render(request, self.template_name, {'error': None})

    def post(self, request):
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        if not (full_name and email and password and password_confirm):
            return render(request, self.template_name, {'error': 'Заполните все поля', 'full_name': full_name, 'email': email})

        if password != password_confirm:
            return render(request, self.template_name, {'error': 'Пароли не совпадают', 'full_name': full_name, 'email': email})

        UserModel = get_user_model()
        if UserModel.objects.filter(email=email).exists():
            return render(request, self.template_name, {'error': 'Такой email уже зарегистрирован', 'full_name': full_name, 'email': email})

        user = UserModel.objects.create_user(username=email, email=email, password=password, first_name=full_name)
        
        # Check for anonymous cart BEFORE login
        session_key = request.session.session_key
        anon_cart = None
        if session_key:
            from basket.models import Cart
            anon_cart = Cart.objects.filter(session_key=session_key, user__isnull=True).first()

        login(request, user)

        # Merge carts after login
        if anon_cart:
            user_cart, _ = Cart.objects.get_or_create(user=user)
            for item in anon_cart.items.all():
                # Check if item exists in user_cart
                existing_item = user_cart.items.filter(product=item.product, size=item.size).first()
                if existing_item:
                    existing_item.quantity += item.quantity
                    existing_item.save()
                else:
                    item.cart = user_cart
                    item.save()
            anon_cart.delete()

        return redirect(reverse('catalog:profile'))


def logout_view(request):
    logout(request)
    return redirect(reverse('users:login'))


class ProfileUpdateView(LoginRequiredMixin, View):
    def post(self, request):
        user = request.user
        full_name = request.POST.get('full_name', '').strip()
        avatar = request.FILES.get('avatar')

        if full_name:
            parts = full_name.split(None, 1)
            user.first_name = parts[0]
            user.last_name = parts[1] if len(parts) > 1 else ''

        if avatar:
            user.avatar = avatar

        user.save()
        messages.success(request, 'Профиль обновлен')

        next_url = request.POST.get('next') or reverse('catalog:profile')
        return redirect(next_url)
