from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'feedstock', views.FeedstockViewSet, basename='feedstock')
router.register(r'digestate', views.DigestateViewSet, basename='digestate')

urlpatterns = [
    path('', include(router.urls)),
]
