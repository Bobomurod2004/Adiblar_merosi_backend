from django.db.models import Prefetch
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from apps.works.models import LiteraryWork
from .models import Writer
from .serializers import WriterListSerializer, WriterDetailSerializer


class WriterListView(generics.ListAPIView):
    """Get all writers"""
    queryset = Writer.objects.filter(is_active=True)
    serializer_class = WriterListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ['is_active']
    search_fields = ['first_name', 'last_name', 'short_bio']
    ordering_fields = ['birth_date', 'created_at']
    ordering = ['birth_date']


class WriterDetailView(generics.RetrieveAPIView):
    """Get single writer with details"""
    queryset = Writer.objects.filter(is_active=True).prefetch_related(
        Prefetch(
            'works',
            queryset=LiteraryWork.objects.filter(is_published=True).select_related('genre').order_by('-publication_year', 'title'),
            to_attr='published_works',
        )
    )
    serializer_class = WriterDetailSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticatedOrReadOnly]
