from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Writer


class WriterAdmin(ModelAdmin):
    """Yozuvchilar admin"""
    list_display = ('full_name', 'birth_date', 'death_date', 'is_active', 'created_at')
    list_filter = ('is_active', 'birth_date', 'created_at')
    search_fields = ('first_name', 'last_name', 'short_bio')
    readonly_fields = ('slug', 'created_at', 'updated_at')
    date_hierarchy = 'birth_date'

    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('first_name', 'last_name', 'slug', 'image')
        }),
        ('Biografiya', {
            'fields': ('short_bio', 'detailed_bio')
        }),
        ('Hayoti', {
            'fields': ('birth_date', 'birth_place', 'death_date', 'death_place')
        }),
        ('Ijodiy ma\'lumotlar', {
            'fields': ('creative_period_start', 'creative_period_end', 'main_genres',
                      'influenced_by', 'influenced', 'legacy')
        }),
        ('Holati', {
            'fields': ('is_active',)
        }),
        ('Teknikaviy', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """Slug ni avtomatik yaratish"""
        super().save_model(request, obj, form, change)


if Writer not in admin.site._registry:
    admin.site.register(Writer, WriterAdmin)

