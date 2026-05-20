from rest_framework import serializers
from .models import LiteraryGenre, LiteraryWork, BookFile
from apps.writers.serializers import WriterListSerializer
from apps.common.media import safe_media_url


class LiteraryGenreSerializer(serializers.ModelSerializer):
    """Literary Genres"""
    class Meta:
        model = LiteraryGenre
        fields = ('id', 'name', 'slug', 'description')


class BookFileSerializer(serializers.ModelSerializer):
    """Book Files - PDF, EPUB, TXT"""
    file = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = BookFile
        fields = ('id', 'file_type', 'file', 'pages_count', 'file_size', 'language')

    def get_file(self, obj):
        return safe_media_url(getattr(obj, 'file', None))


class WorkListSerializer(serializers.ModelSerializer):
    """Literary Works - List view"""
    writer = WriterListSerializer(read_only=True)
    genre = LiteraryGenreSerializer(read_only=True)
    has_book_file = serializers.SerializerMethodField()
    book_file_type = serializers.SerializerMethodField()
    cover_image = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = LiteraryWork
        fields = (
            'id', 'slug', 'title', 'writer', 'genre', 'description',
            'publication_year', 'cover_image', 'views_count', 'rating', 'is_featured',
            'has_book_file', 'book_file_type'
        )

    def get_has_book_file(self, obj):
        book_file = getattr(obj, 'book_file', None)
        if not book_file:
            return False
        return bool(safe_media_url(getattr(book_file, 'file', None)))

    def get_book_file_type(self, obj):
        if self.get_has_book_file(obj):
            return obj.book_file.file_type
        return None

    def get_cover_image(self, obj):
        return safe_media_url(getattr(obj, 'cover_image', None))


class WorkDetailSerializer(serializers.ModelSerializer):
    """Literary Works - Detail view"""
    writer = WriterListSerializer(read_only=True)
    genre = LiteraryGenreSerializer(read_only=True)
    book_file = BookFileSerializer(read_only=True)
    cover_image = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = LiteraryWork
        fields = (
            'id', 'slug', 'title', 'writer', 'genre', 'description', 'introduction',
            'content', 'publication_year', 'original_language', 'cover_image',
            'views_count', 'downloads_count', 'rating', 'is_featured', 'is_published',
            'book_file', 'created_at', 'updated_at'
        )
        read_only_fields = ('views_count', 'downloads_count', 'created_at', 'updated_at')

    def get_cover_image(self, obj):
        return safe_media_url(getattr(obj, 'cover_image', None))
