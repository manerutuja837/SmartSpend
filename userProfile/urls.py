# urls.py

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import profile_view,profile_add

urlpatterns = [
    path('', profile_view, name='profile_view'),  # Profile view URL
    path('edit_profile/', profile_add, name='profile'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)