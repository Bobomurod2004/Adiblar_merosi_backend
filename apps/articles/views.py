from django.utils import timezone
from django.core.cache import cache
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.response import Response
from .models import Tag, Article
from .serializers import TagSerializer, ArticleListSerializer, ArticleDetailSerializer, ArticleCreateSerializer


class TagListView(generics.ListAPIView):
	queryset = Tag.objects.all()
	serializer_class = TagSerializer
	permission_classes = [IsAuthenticatedOrReadOnly]


class ArticleListView(generics.ListAPIView):
	serializer_class = ArticleListSerializer
	permission_classes = [IsAuthenticatedOrReadOnly]

	def get_queryset(self):
		return Article.objects.filter(status='published').select_related('author', 'writer').prefetch_related('tags')


class ArticleHomeListView(generics.ListAPIView):
	"""
	Bosh sahifadagi mini-panel uchun oxirgi 3 ta e'lon qilingan maqola.
	Paginatsiya o'chirilgan: frontendga faqat kerakli, ixcham ro'yxat qaytariladi.
	"""
	serializer_class = ArticleListSerializer
	permission_classes = [IsAuthenticatedOrReadOnly]
	pagination_class = None
	filter_backends = []

	def get_queryset(self):
		return (
			Article.objects.filter(status='published')
			.select_related('author', 'writer')
			.prefetch_related('tags')
			.order_by('-published_at', '-created_at')[:3]
		)


class ArticleDetailView(generics.RetrieveAPIView):
	serializer_class = ArticleDetailSerializer
	permission_classes = [IsAuthenticatedOrReadOnly]
	lookup_field = 'slug'

	def get_queryset(self):
		return Article.objects.filter(status='published').select_related('author', 'writer').prefetch_related('tags', 'comments')

	def _should_increment_view(self, request, article_id):
		"""
		StrictMode yoki tez-tez takror request holatida bir session ichida
		qisqa vaqt davomida view ni bir martadan oshirmaslik.
		"""
		session_key = request.session.session_key
		if not session_key:
			request.session.create()
			session_key = request.session.session_key

		user_part = f"user:{request.user.id}" if request.user.is_authenticated else "anon"
		cache_key = f"article_view:{article_id}:{user_part}:{session_key}"

		if cache.get(cache_key):
			return False

		cache.set(cache_key, True, timeout=60)
		return True

	def retrieve(self, request, *args, **kwargs):
		instance = self.get_object()
		if self._should_increment_view(request, instance.id):
			instance.increment_views()
		serializer = self.get_serializer(instance)
		return Response(serializer.data)


class ArticleCreateView(generics.CreateAPIView):
	serializer_class = ArticleCreateSerializer
	permission_classes = [IsAuthenticatedOrReadOnly]


class ArticleApproveView(generics.UpdateAPIView):
	queryset = Article.objects.all()
	serializer_class = ArticleDetailSerializer
	permission_classes = [IsAdminUser]
	lookup_field = 'id'

	def update(self, request, *args, **kwargs):
		article = self.get_object()
		article.status = 'published'
		article.published_at = timezone.now()
		article.save(update_fields=['status', 'published_at', 'updated_at'])
		return Response(ArticleDetailSerializer(article).data)


class ArticleRejectView(generics.UpdateAPIView):
	queryset = Article.objects.all()
	serializer_class = ArticleDetailSerializer
	permission_classes = [IsAdminUser]
	lookup_field = 'id'

	def update(self, request, *args, **kwargs):
		article = self.get_object()
		article.status = 'rejected'
		article.admin_notes = request.data.get('admin_notes', '')
		article.save(update_fields=['status', 'admin_notes', 'updated_at'])
		return Response(ArticleDetailSerializer(article).data)


class UserArticleListView(generics.ListAPIView):
	"""
	Foydalanuvchining o'zi yuborgan maqolalar ro'yxati (holati bilan birga).
	"""
	serializer_class = ArticleListSerializer
	permission_classes = [IsAuthenticatedOrReadOnly]

	def get_queryset(self):
		return (
			Article.objects.filter(author=self.request.user)
			.select_related('author', 'writer')
			.prefetch_related('tags')
			.order_by('-created_at')
		)
