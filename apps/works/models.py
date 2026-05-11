from django.db import models
from django.utils.text import slugify
from apps.common.models import BaseModel
from apps.writers.models import Writer


class LiteraryGenre(models.Model):
    """Janrlar - Sheriyat, Nasir, Drama va boshqalar"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nomi")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Tavsifi")
    
    class Meta:
        verbose_name = "Janr"
        verbose_name_plural = "Janrlar"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class LiteraryWork(BaseModel):
    """
    Adabiy asar - sheriyat, nasir, drama va boshqalar
    """
    title = models.CharField(max_length=255, verbose_name="Sarlavhasi")
    slug = models.SlugField(unique=True, null=True, blank=True, verbose_name="URL slug")
    writer = models.ForeignKey(
        Writer,
        on_delete=models.CASCADE,
        related_name='works',
        verbose_name="Muallifi"
    )
    
    genre = models.ForeignKey(
        LiteraryGenre,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='works',
        verbose_name="Janri"
    )
    
    # Asarning ma'lumotlari
    description = models.TextField(verbose_name="Qisqa tavsifi")
    introduction = models.TextField(blank=True, verbose_name="Muqaddima/Kontekst")
    
    # Asarning matni
    content = models.TextField(verbose_name="Matn") # HTML/Markdown da bo'ladi
    
    # Nashr ma'lumotlari
    publication_year = models.IntegerField(verbose_name="Nashr yili")
    original_language = models.CharField(
        max_length=50,
        default='Uzbek',
        verbose_name="Asl tili"
    )
    
    # Metadatalar
    views_count = models.IntegerField(default=0, verbose_name="Ko'rishlar soni")
    downloads_count = models.IntegerField(default=0, verbose_name="Yuklab olinishlar soni")
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        verbose_name="Reytingi"
    )
    
    # Tasavvur
    cover_image = models.ImageField(
        upload_to='works/covers/',
        null=True,
        blank=True,
        verbose_name="Muqova rasmi"
    )
    
    is_featured = models.BooleanField(default=False, verbose_name="Asosiy asar")
    is_published = models.BooleanField(default=True, verbose_name="Eʼlon qilingan")
    
    class Meta:
        ordering = ['-publication_year', 'title']
        verbose_name = "Adabiy asar"
        verbose_name_plural = "Adabiy asarlar"
        indexes = [
            models.Index(fields=['writer', 'publication_year']),
            models.Index(fields=['slug']),
            models.Index(fields=['is_published']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.writer.full_name} ({self.publication_year})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.publication_year}")
        super().save(*args, **kwargs)
    
    def increment_views(self):
        """Ko'rishlar sonini oʻnritma"""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def increment_downloads(self):
        """Yuklab olinishlar sonini oʻnritma"""
        self.downloads_count += 1
        self.save(update_fields=['downloads_count'])


class BookFile(BaseModel):
    """
    Asar fayli (PDF, EPUB, TXT)
    """
    FILE_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('epub', 'EPUB'),
        ('txt', 'Text'),
        ('html', 'HTML'),
    ]
    
    work = models.OneToOneField(
        LiteraryWork,
        on_delete=models.CASCADE,
        related_name='book_file',
        verbose_name="Asar"
    )
    
    file_type = models.CharField(
        max_length=10,
        choices=FILE_TYPE_CHOICES,
        default='pdf',
        verbose_name="Fayl turi"
    )
    
    file = models.FileField(
        upload_to='works/files/',
        verbose_name="Fayl"
    )
    
    pages_count = models.IntegerField(null=True, blank=True, verbose_name="Sahifalar soni")
    file_size = models.IntegerField(help_text="Bytes da", verbose_name="Fayl hajmi")
    language = models.CharField(max_length=50, default='Uzbek', verbose_name="Tili")
    
    class Meta:
        verbose_name = "Kitob fayli"
        verbose_name_plural = "Kitob fayllar"
    
    def save(self, *args, **kwargs):
        if self.file and not self.file_size:
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.work.title} ({self.get_file_type_display()})"

