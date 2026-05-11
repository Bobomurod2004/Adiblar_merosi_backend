from django.urls import path
from .views import (
    WorkListView, WorkDetailView, WorkDownloadView,
    GenreListView, BookFileViewSet
)

app_name = 'works'

urlpatterns = [
    # Literary Genres
    path('genres/', GenreListView.as_view(), name='genre-list'),
    
    # Literary Works
    path('', WorkListView.as_view(), name='work-list'),
    path('<slug:slug>/', WorkDetailView.as_view(), name='work-detail'),
    path('<int:id>/download/', WorkDownloadView.as_view(), name='work-download'),
    
    # Book Files
    path('files/<int:id>/preview/', BookFileViewSet.as_view({'get': 'preview'}), name='book-preview'),
]
