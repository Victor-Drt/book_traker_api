from django.urls import path, include

from rest_framework import routers

from .views import BookViewSet, StatsViewSet

router = routers.DefaultRouter()
router.register(r'books', BookViewSet, basename='books')
router.register(r'stats', StatsViewSet, basename='stats')

urlpatterns = [
    path('', include(router.urls)),
]
