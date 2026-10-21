from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'production', views.ProductionLogViewSet, basename='production')

analytics_view = views.AnalyticsView.as_view()

urlpatterns = [
    path('', include(router.urls)),
    path('live/', analytics_view, {'action': 'live'}),
    path('history/', analytics_view, {'action': 'history'}),
    path('methane-prediction/', analytics_view, {'action': 'methane-prediction'}),
    path('daily-report/', analytics_view, {'action': 'daily-report'}),
    path('monthly-report/', analytics_view, {'action': 'monthly-report'}),
]
