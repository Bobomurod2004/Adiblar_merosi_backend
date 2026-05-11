from django.db import models
from django.contrib.auth.models import User
from apps.common.models import BaseModel


class UserProfile(BaseModel):
    """
    Foydalanuvchi profili (User extension)
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name="Foydalanuvchi"
    )
    
    avatar = models.ImageField(
        upload_to='users/avatars/',
        null=True,
        blank=True,
        verbose_name="Avatari"
    )
    
    bio = models.TextField(
        blank=True,
        max_length=500,
        verbose_name="Biografiya"
    )
    
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Telefon raqami"
    )
    
    website = models.URLField(
        blank=True,
        verbose_name="Veb-sayt"
    )
    
    location = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Manzili"
    )
    
    telegram_username = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Telegram username"
    )
    
    # Statistika
    article_count = models.IntegerField(default=0, verbose_name="Maqolalar soni")
    joined_date = models.DateTimeField(auto_now_add=True, verbose_name="Ruyxatlanish sanasi")
    
    # Notifikatsiyalar
    receive_email_notifications = models.BooleanField(
        default=True,
        verbose_name="Email xabarlari"
    )
    
    class Meta:
        verbose_name = "Foydalanuvchi profili"
        verbose_name_plural = "Foydalanuvchi profillari"
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - Profili"


class Bookmark(BaseModel):
    """
    Foydalanuvchining saqlangan asarlar (bookmark)
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookmarks',
        verbose_name="Foydalanuvchi"
    )
    
    work = models.ForeignKey(
        'works.LiteraryWork',
        on_delete=models.CASCADE,
        related_name='bookmarked_by',
        verbose_name="Asar"
    )
    
    note = models.TextField(
        blank=True,
        verbose_name="Izoh"
    )
    
    class Meta:
        unique_together = ('user', 'work')
        verbose_name = "Saqlangan asar"
        verbose_name_plural = "Saqlangan asarlar"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.work.title}"

