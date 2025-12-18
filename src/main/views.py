from django.shortcuts import render
from django.views import View

from basket.models import Order
from catalog.models import Brand, Category, HomepageBlock, Review


class GeneralPageView(View):
    def get(self, request):
        categories = Category.objects.all()
        blocks = HomepageBlock.objects.filter(is_active=True).exclude(block_type='hero').order_by('sort_order')
        hero_block = HomepageBlock.objects.filter(block_type='hero', is_active=True).first()
        reviews = Review.objects.filter(status='approved').order_by('-created_at')[:6]
        return render(request, 'main/general.html', {
            'categories': categories,
            'blocks': blocks,
            'reviews': reviews,
            'hero_block': hero_block
        })
    
    def post(self, request):
        # Handle review submission
        name = request.POST.get('name')
        city = request.POST.get('city')
        rating = request.POST.get('rating')
        text = request.POST.get('text')
        
        if name and city and rating and text:
            Review.objects.create(
                name=name,
                city=city,
                rating=int(rating),
                text=text,
                status='pending'
            )
        
        from django.http import JsonResponse
        return JsonResponse({'success': True, 'message': 'Спасибо за отзыв! Он будет опубликован после модерации.'})


class BrandPageView(View):
    def get(self, request):
        brands = Brand.objects.filter(is_active=True).order_by('sort_order', 'name')
        return render(request, 'main/brand.html', {'brands': brands})


class ProjectPageView(View):
    def get(self, request):
        return render(request, 'main/project.html')


from django.http import JsonResponse
import json

class NewsletterSubscribeView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email')
            
            if not email:
                return JsonResponse({'success': False, 'message': 'Email обязателен'}, status=400)
            
            from django.core.validators import validate_email
            from django.core.exceptions import ValidationError
            
            try:
                validate_email(email)
            except ValidationError:
                 return JsonResponse({'success': False, 'message': 'Некорректный email'}, status=400)

            from .models import NewsletterSubscriber
            obj, created = NewsletterSubscriber.objects.get_or_create(email=email)
            
            if not created:
                 if not obj.is_active:
                     obj.is_active = True
                     obj.save()
                     return JsonResponse({'success': True, 'message': 'Вы снова подписались!'})
                 return JsonResponse({'success': False, 'message': 'Вы уже подписаны'}, status=400)
            
            return JsonResponse({'success': True, 'message': 'Спасибо за подписку!'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
