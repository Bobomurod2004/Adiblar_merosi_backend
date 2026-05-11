from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from .models import Tag, Article, ArticleComment


class ArticleCommentInline(TabularInline):
    """ArticleComment inline"""
    model = ArticleComment
    extra = 0
    fields = ('author', 'content', 'is_approved', 'created_at')
    readonly_fields = ('author', 'content', 'created_at')
    can_delete = True


class TagAdmin(ModelAdmin):
    """Teglar admin"""
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class ArticleAdmin(ModelAdmin):
    """Maqolalar admin"""
    list_display = ('title', 'author', 'writer', 'status_badge', 'views_count', 'submitted_at')
    list_filter = ('status', 'writer', 'submitted_at', 'published_at', 'created_at')
    search_fields = ('title', 'content', 'author__username', 'author__email')
    filter_horizontal = ('tags',)
    readonly_fields = ('slug', 'views_count', 'created_at', 'updated_at', 'submitted_at', 'published_at')
    inlines = [ArticleCommentInline]
    date_hierarchy = 'submitted_at'

    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('title', 'slug', 'author', 'writer')
        }),
        ('Maqola matni', {
            'fields': ('summary', 'content', 'featured_image', 'article_file')
        }),
        ('Metadata', {
            'fields': ('tags', 'views_count')
        }),
        ('Status va moderatsiya', {
            'fields': ('status', 'admin_notes')
        }),
        ('Vaqtlar', {
            'fields': ('submitted_at', 'published_at'),
            'classes': ('collapse',)
        }),
        ('Teknikaviy', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['approve_articles', 'reject_articles']

    def status_badge(self, obj):
        """Status badges"""
        colors = {
            'draft': '#6B7280',
            'pending': '#F59E0B',
            'published': '#10B981',
            'rejected': '#EF4444',
        }
        status_names = {
            'draft': 'Qoralamaʼ',
            'pending': 'Kutilmoqda',
            'published': 'Eʼlon qilingan',
            'rejected': 'Rad etilgan',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#6B7280'),
            status_names.get(obj.status, obj.status)
        )
    status_badge.short_description = 'Holati'

    def approve_articles(self, request, queryset):
        """Maqolalarni tasdiqlash"""
        for article in queryset.filter(status='pending'):
            article.publish()
        self.message_user(request, f"{queryset.count()} maqola eʼlon qilindi.")
    approve_articles.short_description = "Tanlangan maqolalarni tasdiqlash"

    def reject_articles(self, request, queryset):
        """Maqolalarni rad etish"""
        queryset.update(status='rejected')
        self.message_user(request, f"{queryset.count()} maqola rad etildi.")
    reject_articles.short_description = "Tanlangan maqolalarni rad etish"


class ArticleCommentAdmin(ModelAdmin):
    """Sharhlar admin"""
    list_display = ('author', 'article', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at', 'article')
    search_fields = ('author__username', 'content', 'article__title')
    readonly_fields = ('author', 'article', 'content', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Sharh ma\'lumotlar', {
            'fields': ('article', 'author', 'content')
        }),
        ('Status', {
            'fields': ('is_approved',)
        }),
        ('Teknikaviy', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['approve_comments', 'unapprove_comments']

    def approve_comments(self, request, queryset):
        """Sharhlarni tasdiqlash"""
        queryset.update(is_approved=True)
        self.message_user(request, f"{queryset.count()} sharh tasdiqlandi.")
    approve_comments.short_description = "Sharhlarni tasdiqlash"

    def unapprove_comments(self, request, queryset):
        """Sharhlarni rad etish"""
        queryset.update(is_approved=False)
        self.message_user(request, f"{queryset.count()} sharh rad etildi.")
    unapprove_comments.short_description = "Sharhlarni rad etish"


for model, model_admin in [
    (Tag, TagAdmin),
    (Article, ArticleAdmin),
    (ArticleComment, ArticleCommentAdmin),
]:
    if model not in admin.site._registry:
        admin.site.register(model, model_admin)
