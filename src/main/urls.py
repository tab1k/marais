from .views import GeneralPageView, BrandPageView, ProjectPageView
from django.urls import path

urlpatterns = [
    path('', GeneralPageView.as_view(), name='general'),
    path('brand/', BrandPageView.as_view(), name='brand'),
    path('project/', ProjectPageView.as_view(), name='project'),
] 



