from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path('api/sensors/', include('apps.sensors.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
    path('api/economic/', include('apps.economic.urls')),
    path('api/feedstock/', include('apps.feedstock.urls')),
    path('api/alerts/', include('apps.alerts.urls')),
    path('api/process/', include('apps.process.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
