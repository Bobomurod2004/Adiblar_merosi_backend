from django.contrib import admin
from django.contrib import messages
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
        """
        Supabase storage xatosida admin 500 bermasligi uchun yumshoq fallback:
        matnli o'zgarishlar saqlanadi, rasm oldingi qiymatda qoladi.
        """
        previous_image_name = None
        if change and obj.pk:
            previous_image_name = (
                Writer.objects.filter(pk=obj.pk).values_list("image", flat=True).first() or ""
            )

        try:
            super().save_model(request, obj, form, change)
        except Exception as exc:
            if "image" not in getattr(form, "changed_data", []):
                raise

            obj.image = previous_image_name or None
            super().save_model(request, obj, form, change)
            self.message_user(
                request,
                f"Rasm Supabase'ga yuklanmadi ({exc}). Qolgan o'zgarishlar saqlandi.",
                level=messages.WARNING,
            )


if Writer not in admin.site._registry:
    admin.site.register(Writer, WriterAdmin)
