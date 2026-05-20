"""
URL configuration for Adiblar Merosi project.

Main URL router
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from apps.common.media_views import serve_media_file

urlpatterns = [
    # Admin Panel (Django Unfold)
    path('admin/', admin.site.urls),
    
    # API Documentation (Swagger + ReDoc)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc-ui'),
    
    # API v1 Endpoints
    path('api/v1/', include([
        # Writers
        path('writers/', include('apps.writers.urls')),
        
        # Literary Works & Books
        path('works/', include('apps.works.urls')),
        
        # Articles
        path('articles/', include('apps.articles.urls')),
        
        # Users & Authentication
        path('users/', include('apps.users.urls')),

        # Common resources (scholarships/tests/ai chat)
        path('meta/', include('apps.common.urls')),
    ])),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
elif getattr(settings, 'SERVE_MEDIA', False):
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve_media_file),
    ]
