from rest_framework import serializers
from .models import Writer
from apps.works.models import LiteraryWork


class WriterWorkSerializer(serializers.ModelSerializer):
    """Adibning asarlari uchun qisqa serializer"""
    genre_name = serializers.CharField(source='genre.name', read_only=True)

    class Meta:
        model = LiteraryWork
        fields = (
            'id',
            'slug',
            'title',
            'publication_year',
            'genre_name',
            'cover_image',
            'rating',
        )


class WriterListSerializer(serializers.ModelSerializer):
    """Writers - List view"""
    full_name = serializers.CharField(read_only=True)
    years_display = serializers.CharField(read_only=True)
    
    class Meta:
        model = Writer
        fields = ('id', 'slug', 'full_name', 'years_display', 'image', 'short_bio', 'is_active')


class WriterDetailSerializer(serializers.ModelSerializer):
    """Writers - Detail view"""
    full_name = serializers.CharField(read_only=True)
    years_display = serializers.CharField(read_only=True)
    works_count = serializers.SerializerMethodField(read_only=True)
    works = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Writer
        fields = (
            'id', 'slug', 'first_name', 'last_name', 'full_name', 'years_display',
            'image', 'short_bio', 'detailed_bio', 'birth_date', 'death_date',
            'birth_place', 'death_place', 'creative_period_start', 'creative_period_end',
            'main_genres', 'influenced_by', 'influenced', 'legacy', 'works_count', 'works',
            'is_active'
        )
    
    def get_works_count(self, obj):
        """Yozuvchining asarlar soni"""
        if hasattr(obj, 'published_works'):
            return len(obj.published_works)
        return obj.works.filter(is_published=True).count()

    def get_works(self, obj):
        """Yozuvchining e'lon qilingan asarlari"""
        works = getattr(obj, 'published_works', None)
        if works is None:
            works = obj.works.filter(is_published=True).select_related('genre').order_by('-publication_year', 'title')
        return WriterWorkSerializer(works, many=True, context=self.context).data
