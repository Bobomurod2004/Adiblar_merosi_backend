from django.db.models import Prefetch
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from apps.works.models import LiteraryWork
from .models import Writer
from .serializers import WriterListSerializer, WriterDetailSerializer, WriterWriteSerializer


class WriterListView(generics.ListCreateAPIView):
    """Get all writers / create new writer"""
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filterset_fields = ['is_active']
    search_fields = ['first_name', 'last_name', 'short_bio']
    ordering_fields = ['birth_date', 'created_at']
    ordering = ['birth_date']

    def get_queryset(self):
        if self.request.method == 'GET':
            return Writer.objects.filter(is_active=True)
        return Writer.objects.all()

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticatedOrReadOnly()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return WriterListSerializer
        return WriterWriteSerializer


class WriterDetailView(generics.RetrieveUpdateAPIView):
    """Get single writer with details / update writer"""
    lookup_field = 'slug'
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        base_queryset = Writer.objects.prefetch_related(
            Prefetch(
                'works',
                queryset=LiteraryWork.objects.filter(is_published=True).select_related('genre').order_by('-publication_year', 'title'),
                to_attr='published_works',
            )
        )
        if self.request.method == 'GET':
            return base_queryset.filter(is_active=True)
        return base_queryset

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticatedOrReadOnly()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return WriterDetailSerializer
        return WriterWriteSerializer
