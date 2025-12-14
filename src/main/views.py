from django.shortcuts import render
from django.views import View

from basket.models import Order
from catalog.models import Brand, Category, HomepageBlock, Review


class GeneralPageView(View):
    def get(self, request):
        categories = Category.objects.all()
        blocks = HomepageBlock.objects.filter(is_active=True).order_by('sort_order')
        reviews = Review.objects.filter(status='approved').order_by('-created_at')[:6]
        return render(request, 'main/general.html', {
            'categories': categories,
            'blocks': blocks,
            'reviews': reviews
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
