from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from apps.common.models import BaseModel
from apps.writers.models import Writer


class Tag(models.Model):
    """
    Kalit so'zlar (Tags)
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Nomi")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    
    class Meta:
        verbose_name = "Teg"
        verbose_name_plural = "Teglar"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Article(BaseModel):
    """
    Foydalanuvchi tomonidan yuborilgan maqola
    """
    STATUS_CHOICES = [
        ('draft', 'Qoralamaʼ'),
        ('pending', 'Kutilmoqda'),
        ('published', 'Eʼlon qilingan'),
        ('rejected', 'Rad etilgan'),
    ]
    
    title = models.CharField(max_length=255, verbose_name="Sarlavhasi")
    slug = models.SlugField(unique=True, null=True, blank=True, verbose_name="URL slug")
    
    # Muallif
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='articles',
        verbose_name="Muallifi"
    )
    
    # Haqida yozuvchi
    writer = models.ForeignKey(
        Writer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles_about',
        verbose_name="Haqida yozuvchi"
    )
    
    # Maqola matni
    summary = models.TextField(max_length=500, verbose_name="Qisqa tavsifi")
    content = models.TextField(verbose_name="Matn") # HTML/Markdown
    
    # Metadatalar
    tags = models.ManyToManyField(Tag, blank=True, related_name='articles', verbose_name="Teglar")
    featured_image = models.ImageField(
        upload_to='articles/images/',
        null=True,
        blank=True,
        verbose_name="Asosiy rasmi"
    )
    article_file = models.FileField(
        upload_to='articles/files/',
        null=True,
        blank=True,
        verbose_name="Maqola fayli"
    )
    
    # Status
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="Holati"
    )
    
    # Admin tomonidan izohlar
    admin_notes = models.TextField(
        blank=True,
        verbose_name="Admin izohoti"
    )
    
    # Vaqtlar
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name="Yuborilgan vaqti")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Eʼlon qilingan vaqti")
    
    # Statistika
    views_count = models.IntegerField(default=0, verbose_name="Ko'rishlar soni")
    
    class Meta:
        ordering = ['-published_at', '-submitted_at', '-created_at']
        verbose_name = "Maqola"
        verbose_name_plural = "Maqolalar"
        indexes = [
            models.Index(fields=['status', '-published_at']),
            models.Index(fields=['writer', 'status']),
            models.Index(fields=['slug']),
            models.Index(fields=['author', 'status']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.author.get_full_name() or self.author.username}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Holat e'lon qilingan bo'lsa va sana yo'q bo'lsa, avtomatik to'ldirish
        if self.status == 'published' and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
            
        super().save(*args, **kwargs)
    
    def publish(self):
        """Maqolani eʼlon qilish"""
        from django.utils import timezone
        self.status = 'published'
        self.published_at = timezone.now()
        self.save()
    
    def reject(self, admin_notes=''):
        """Maqolani rad etish"""
        self.status = 'rejected'
        self.admin_notes = admin_notes
        self.save()
    
    def increment_views(self):
        """Ko'rishlar sonini oʻnritma"""
        self.views_count += 1
        self.save(update_fields=['views_count'])


class ArticleComment(BaseModel):
    """
    Maqolalar ostidagi sharhlar (kommentlar)
    """
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Maqola"
    )
    
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='article_comments',
        verbose_name="Muallifi"
    )
    
    content = models.TextField(verbose_name="Matn")
    
    # Moderatsiya
    is_approved = models.BooleanField(default=True, verbose_name="Tasdiqlangan")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Sharh"
        verbose_name_plural = "Sharhlar"
        indexes = [
            models.Index(fields=['article', 'is_approved']),
        ]
    
    def __str__(self):
        return f"Sharh: {self.author.username} - {self.article.title}"
