from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'optimization', views.ProcessOptimizationViewSet, basename='process-optimization')

urlpatterns = [
    path('', include(router.urls)),
]
