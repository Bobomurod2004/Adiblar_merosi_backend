from rest_framework import serializers
from .models import LiteraryGenre, LiteraryWork, BookFile
from apps.writers.serializers import WriterListSerializer


class LiteraryGenreSerializer(serializers.ModelSerializer):
    """Literary Genres"""
    class Meta:
        model = LiteraryGenre
        fields = ('id', 'name', 'slug', 'description')


class BookFileSerializer(serializers.ModelSerializer):
    """Book Files - PDF, EPUB, TXT"""
    class Meta:
        model = BookFile
        fields = ('id', 'file_type', 'file', 'pages_count', 'file_size', 'language')


class WorkListSerializer(serializers.ModelSerializer):
    """Literary Works - List view"""
    writer = WriterListSerializer(read_only=True)
    genre = LiteraryGenreSerializer(read_only=True)
    has_book_file = serializers.SerializerMethodField()
    book_file_type = serializers.SerializerMethodField()
    
    class Meta:
        model = LiteraryWork
        fields = (
            'id', 'slug', 'title', 'writer', 'genre', 'description',
            'publication_year', 'cover_image', 'views_count', 'rating', 'is_featured',
            'has_book_file', 'book_file_type'
        )

    def get_has_book_file(self, obj):
        return hasattr(obj, 'book_file')

    def get_book_file_type(self, obj):
        if hasattr(obj, 'book_file'):
            return obj.book_file.file_type
        return None


class WorkDetailSerializer(serializers.ModelSerializer):
    """Literary Works - Detail view"""
    writer = WriterListSerializer(read_only=True)
    genre = LiteraryGenreSerializer(read_only=True)
    book_file = BookFileSerializer(read_only=True)
    
    class Meta:
        model = LiteraryWork
        fields = (
            'id', 'slug', 'title', 'writer', 'genre', 'description', 'introduction',
            'content', 'publication_year', 'original_language', 'cover_image',
            'views_count', 'downloads_count', 'rating', 'is_featured', 'is_published',
            'book_file', 'created_at', 'updated_at'
        )
        read_only_fields = ('views_count', 'downloads_count', 'created_at', 'updated_at')
