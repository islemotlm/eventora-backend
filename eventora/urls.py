from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/', include('accounts.admin_urls')),
    path('api/', include('events.urls')),
    path('api/', include('participants.urls')),
    path('api/', include('organizers.urls')),
    path('api/', include('sponsors.urls')),
    path('api/', include('speakers.urls')),
    path('api/', include('attestations.urls')),
    path('api/', include('stats.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
