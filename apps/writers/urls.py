from django.urls import path
from .views import WriterListView, WriterDetailView

app_name = 'writers'

urlpatterns = [
    # List all writers
    path('', WriterListView.as_view(), name='writer-list'),
    
    # Get single writer with details
    path('<slug:slug>/', WriterDetailView.as_view(), name='writer-detail'),
]
