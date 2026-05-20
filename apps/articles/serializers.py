# pyrefly: ignore [missing-import]
from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Tag, Article, ArticleComment
# pyrefly: ignore [missing-import]
from apps.writers.serializers import WriterListSerializer
from apps.common.media import safe_media_url


class TagSerializer(serializers.ModelSerializer):
    """Tags/Keywords"""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class AuthorSerializer(serializers.ModelSerializer):
    """Article Author Info"""
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class ArticleCommentSerializer(serializers.ModelSerializer):
    """Article Comments"""
    author = AuthorSerializer(read_only=True)
    
    class Meta:
        model = ArticleComment
        fields = ('id', 'author', 'content', 'is_approved', 'created_at')
        read_only_fields = ('author', 'is_approved', 'created_at')


class ArticleListSerializer(serializers.ModelSerializer):
    """Articles - List view"""
    author = AuthorSerializer(read_only=True)
    writer = WriterListSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    featured_image = serializers.SerializerMethodField(read_only=True)
    article_file = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Article
        fields = (
            'id', 'slug', 'title', 'author', 'writer', 'summary',
            'featured_image', 'article_file', 'tags', 'views_count', 
            'published_at', 'created_at', 'status'
        )
        read_only_fields = ('views_count', 'status', 'published_at')

    def get_featured_image(self, obj):
        return safe_media_url(getattr(obj, 'featured_image', None))

    def get_article_file(self, obj):
        return safe_media_url(getattr(obj, 'article_file', None))


class ArticleDetailSerializer(serializers.ModelSerializer):
    """Articles - Detail view"""
    author = AuthorSerializer(read_only=True)
    writer = WriterListSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments = ArticleCommentSerializer(many=True, read_only=True)
    featured_image = serializers.SerializerMethodField(read_only=True)
    article_file = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Article
        fields = (
            'id', 'slug', 'title', 'author', 'writer', 'summary', 'content',
            'featured_image', 'article_file', 'tags', 'comments', 'views_count', 'status',
            'submitted_at', 'published_at', 'created_at', 'updated_at'
        )
        read_only_fields = ('views_count', 'status', 'submitted_at', 'published_at', 'created_at', 'updated_at')

    def get_featured_image(self, obj):
        return safe_media_url(getattr(obj, 'featured_image', None))

    def get_article_file(self, obj):
        return safe_media_url(getattr(obj, 'article_file', None))


class ArticleCreateSerializer(serializers.ModelSerializer):
    """Article creation/update"""
    submit_for_review = serializers.BooleanField(write_only=True, required=False, default=True)
    tags_data = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        write_only=True,
        source='tags'
    )
    
    class Meta:
        model = Article
        fields = (
            'title',
            'writer',
            'summary',
            'content',
            'featured_image',
            'article_file',
            'tags_data',
            'submit_for_review',
        )
    
    def create(self, validated_data):
        """Create article with current user as author"""
        submit_for_review = validated_data.pop('submit_for_review', True)

        validated_data['author'] = self.context['request'].user
        validated_data['status'] = 'pending' if submit_for_review else 'draft'
        if submit_for_review:
            validated_data['submitted_at'] = timezone.now()

        return super().create(validated_data)
