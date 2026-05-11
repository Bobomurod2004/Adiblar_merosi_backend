from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as DjangoGroupAdmin, UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group, User
from unfold.admin import ModelAdmin
from .models import UserProfile, Bookmark


class UserProfileAdmin(ModelAdmin):
    """Foydalanuvchi profili admin"""
    list_display = ('user', 'article_count', 'joined_date', 'receive_email_notifications')
    list_filter = ('receive_email_notifications', 'joined_date', 'created_at')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('user', 'article_count', 'joined_date', 'created_at', 'updated_at')
    date_hierarchy = 'joined_date'

    fieldsets = (
        ('Foydalanuvchi', {
            'fields': ('user',)
        }),
        ('Profil ma\'lumotlar', {
            'fields': ('avatar', 'bio', 'phone_number', 'website', 'location')
        }),
        ('Statistika', {
            'fields': ('article_count', 'joined_date')
        }),
        ('Notifikatsiyalar', {
            'fields': ('receive_email_notifications',)
        }),
        ('Teknikaviy', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class BookmarkAdmin(ModelAdmin):
    """Bookmarklar admin"""
    list_display = ('user', 'work', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('user__username', 'work__title')
    readonly_fields = ('user', 'work', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Bookmark ma\'lumotlar', {
            'fields': ('user', 'work')
        }),
        ('Izoh', {
            'fields': ('note',)
        }),
        ('Teknikaviy', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


for model, model_admin in [
    (UserProfile, UserProfileAdmin),
    (Bookmark, BookmarkAdmin),
    (User, DjangoUserAdmin),
    (Group, DjangoGroupAdmin),
]:
    if model not in admin.site._registry:
        admin.site.register(model, model_admin)

