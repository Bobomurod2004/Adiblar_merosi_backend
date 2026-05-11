from rest_framework import serializers
from .models import Writer


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
    
    class Meta:
        model = Writer
        fields = (
            'id', 'slug', 'first_name', 'last_name', 'full_name', 'years_display',
            'image', 'short_bio', 'detailed_bio', 'birth_date', 'death_date',
            'birth_place', 'death_place', 'creative_period_start', 'creative_period_end',
            'main_genres', 'influenced_by', 'influenced', 'legacy', 'works_count', 'is_active'
        )
    
    def get_works_count(self, obj):
        """Yozuvchining asarlar soni"""
        return obj.works.filter(is_published=True).count()
