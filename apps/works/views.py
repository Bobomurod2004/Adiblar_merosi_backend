from rest_framework import generics, viewsets, pagination
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.response import Response
from .models import LiteraryGenre, LiteraryWork, BookFile
from .serializers import LiteraryGenreSerializer, WorkListSerializer, WorkDetailSerializer, BookFileSerializer


class StandardResultsSetPagination(pagination.PageNumberPagination):
	page_size = 10
	page_size_query_param = 'page_size'
	max_page_size = 100


class GenreListView(generics.ListAPIView):
	queryset = LiteraryGenre.objects.all()
	serializer_class = LiteraryGenreSerializer
	permission_classes = [IsAuthenticatedOrReadOnly]


class WorkListView(generics.ListAPIView):
	queryset = LiteraryWork.objects.filter(is_published=True).select_related('writer', 'genre', 'book_file')
	serializer_class = WorkListSerializer
	permission_classes = [IsAuthenticatedOrReadOnly]
	pagination_class = StandardResultsSetPagination
	filter_backends = [DjangoFilterBackend, SearchFilter]
	search_fields = ['title', 'description', 'writer__first_name', 'writer__last_name', 'publication_year']
	filterset_fields = ['genre', 'writer', 'publication_year', 'is_featured']


class WorkDetailView(generics.RetrieveAPIView):
	queryset = LiteraryWork.objects.filter(is_published=True).select_related('writer', 'genre', 'book_file')
	serializer_class = WorkDetailSerializer
	permission_classes = [IsAuthenticatedOrReadOnly]
	lookup_field = 'slug'

	def retrieve(self, request, *args, **kwargs):
		instance = self.get_object()
		instance.increment_views()
		serializer = self.get_serializer(instance)
		return Response(serializer.data)


class WorkDownloadView(generics.RetrieveAPIView):
	queryset = LiteraryWork.objects.filter(is_published=True).select_related('book_file')
	serializer_class = WorkDetailSerializer
	permission_classes = [IsAuthenticatedOrReadOnly]
	lookup_field = 'id'

	def retrieve(self, request, *args, **kwargs):
		instance = self.get_object()
		instance.increment_downloads()
		serializer = self.get_serializer(instance)
		return Response(serializer.data)


class BookFileViewSet(viewsets.ViewSet):
	permission_classes = [IsAuthenticatedOrReadOnly]

	def preview(self, request, id=None):
		try:
			book_file = BookFile.objects.get(pk=id)
		except BookFile.DoesNotExist:
			return Response({'detail': 'Topilmadi'}, status=404)
		serializer = BookFileSerializer(book_file)
		return Response(serializer.data)
