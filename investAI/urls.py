from django.urls import path
from .views import investAI

urlpatterns = [
    path('', investAI, name='investAI'),
]
