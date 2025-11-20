from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('crawl/', views.start_crawl, name='start_crawl'),
    path('presentation/', views.crawler_presentation, name='crawler_presentation'),
]
