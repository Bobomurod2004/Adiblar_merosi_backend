"""
URL configuration for Adiblar Merosi project.

Main URL router
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

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

import os
from django.http import Http404

def serve_media_with_fallback(request, path, document_root=None):
    """
    Primary media root dan faylni qidiradi. Topilmasa,
    Render disk ulanishi mumkin bo'lgan fallback manzillardan qidirib serve qiladi.
    """
    try:
        return serve(request, path, document_root=document_root)
    except Http404:
        pass

    # Fallback papkalar ro'yxati
    fallbacks = [
        '/opt/render/project/src/media',
        '/opt/render/project/src/backend/media',
        '/var/data/media',
    ]
    
    # Environmentdagi fallbacks ni ham qo'shamiz
    env_fallbacks = os.environ.get('MEDIA_ROOT_FALLBACKS', '')
    if env_fallbacks:
        for p in env_fallbacks.split(','):
            cleaned = p.strip()
            if cleaned and cleaned not in fallbacks:
                fallbacks.append(cleaned)

    for fallback_root in fallbacks:
        if os.path.isdir(fallback_root):
            full_path = os.path.join(fallback_root, path)
            if os.path.exists(full_path) and os.path.isfile(full_path):
                return serve(request, path, document_root=fallback_root)

    raise Http404("Fayl topilmadi.")

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
elif getattr(settings, 'SERVE_MEDIA', False):
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve_media_with_fallback, {'document_root': settings.MEDIA_ROOT}),
    ]
