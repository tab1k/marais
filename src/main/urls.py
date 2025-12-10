from .views import *
from django.urls import path

urlpatterns = [
    path('', GeneralPageView.as_view(), name='general'),
] 




