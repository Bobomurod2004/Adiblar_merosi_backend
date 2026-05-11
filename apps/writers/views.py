from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
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
    queryset = Writer.objects.filter(is_active=True)
    serializer_class = WriterDetailSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticatedOrReadOnly]
