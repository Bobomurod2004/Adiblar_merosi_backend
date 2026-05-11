from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import LiteraryGenre, LiteraryWork, BookFile


class BookFileInline(TabularInline):
    """BookFile inline"""
    model = BookFile
    extra = 1
    fields = ('file_type', 'file', 'pages_count', 'language')


class LiteraryGenreAdmin(ModelAdmin):
    """Janrlar admin"""
    list_display = ('name', 'slug')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


class LiteraryWorkAdmin(ModelAdmin):
    """Asarlar admin"""
    list_display = ('title', 'writer', 'genre', 'publication_year', 'is_featured', 'is_published', 'views_count')
    list_filter = ('is_published', 'is_featured', 'genre', 'publication_year', 'writer', 'created_at')
    search_fields = ('title', 'writer__first_name', 'writer__last_name', 'description')
    readonly_fields = ('slug', 'views_count', 'downloads_count', 'created_at', 'updated_at')
    inlines = [BookFileInline]
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('title', 'slug', 'writer', 'genre', 'publication_year')
        }),
        ('Tavsifi', {
            'fields': ('description', 'introduction', 'content', 'original_language')
        }),
        ('Rasmi', {
            'fields': ('cover_image',)
        }),
        ('Metadata', {
            'fields': ('views_count', 'downloads_count', 'rating')
        }),
        ('Status', {
            'fields': ('is_featured', 'is_published')
        }),
        ('Teknikaviy', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """Slug ni avtomatik yaratish"""
        super().save_model(request, obj, form, change)


class BookFileAdmin(ModelAdmin):
    """Kitob fayllar admin"""
    list_display = ('work', 'file_type', 'pages_count', 'file_size', 'language')
    list_filter = ('file_type', 'language', 'created_at')
    search_fields = ('work__title',)
    readonly_fields = ('file_size', 'created_at', 'updated_at')

    fieldsets = (
        ('Fayl ma\'lumotlar', {
            'fields': ('work', 'file_type', 'file', 'file_size')
        }),
        ('Metadata', {
            'fields': ('pages_count', 'language')
        }),
        ('Teknikaviy', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


for model, model_admin in [
    (LiteraryGenre, LiteraryGenreAdmin),
    (LiteraryWork, LiteraryWorkAdmin),
    (BookFile, BookFileAdmin),
]:
    if model not in admin.site._registry:
        admin.site.register(model, model_admin)

