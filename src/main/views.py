from django.shortcuts import render
from django.views import View


class GeneralPageView(View):
    def get(self, request):
        return render(request, 'main/general.html')