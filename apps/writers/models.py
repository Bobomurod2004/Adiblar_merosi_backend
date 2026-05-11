from django.db import models
from django.utils.text import slugify
from django.core.validators import URLValidator
from apps.common.models import BaseModel


class Writer(BaseModel):
    """
    Yozuvchi modeli - Uzbek klassik yozuvchilari
    """
    first_name = models.CharField(max_length=100, verbose_name="Ismi")
    last_name = models.CharField(max_length=100, blank=True, default='', verbose_name="Familiyasi")
    slug = models.SlugField(unique=True, null=True, blank=True, verbose_name="URL slug")
    
    # Rasm
    image = models.ImageField(
        upload_to='writers/images/',
        null=True,
        blank=True,
        verbose_name="Rasmi"
    )
    
    # Biografiya
    short_bio = models.TextField(
        max_length=500,
        verbose_name="Qisqa maʼlumot (Overview)"
    )
    detailed_bio = models.TextField(
        verbose_name="Batafsil biografiya"
    )
    
    # Hayoti
    birth_date = models.DateField(verbose_name="Tug'ilgan sanasi")
    death_date = models.DateField(null=True, blank=True, verbose_name="Vafot etgan sanasi")
    birth_place = models.CharField(max_length=255, verbose_name="Tug'ilgan joyı")
    death_place = models.CharField(max_length=255, null=True, blank=True, verbose_name="Vafot etgan joyı")
    
    # Ijodiy ma'lumotlar
    creative_period_start = models.IntegerField(null=True, blank=True, verbose_name="Ijod davri boshi (yil)")
    creative_period_end = models.IntegerField(null=True, blank=True, verbose_name="Ijod davri oxiri (yil)")
    main_genres = models.CharField(
        max_length=255,
        help_text="Vergul bilan ajratilgan",
        verbose_name="Asosiy janrlar"
    )
    
    # Influenslar
    influenced_by = models.CharField(
        max_length=255,
        blank=True,
        help_text="Vergul bilan ajratilgan",
        verbose_name="Taʼsiri qilgan mutafakkirlar"
    )
    influenced = models.CharField(
        max_length=255,
        blank=True,
        help_text="Vergul bilan ajratilgan",
        verbose_name="Taʼsir qilgan shoxislar"
    )
    
    # Oʻzbek adabiyotidagi oʻrni
    legacy = models.TextField(
        blank=True,
        verbose_name="Merosi va taʼsiri"
    )
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    
    class Meta:
        ordering = ['birth_date']
        verbose_name = "Yozuvchi"
        verbose_name_plural = "Yozuvchilar"
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        name = self.full_name
        return f"{name} ({self.birth_date.year}-{self.death_date.year if self.death_date else '?'})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify("-".join(part for part in [self.first_name, self.last_name] if part))
        super().save(*args, **kwargs)
    
    @property
    def full_name(self):
        return " ".join(part for part in [self.first_name, self.last_name] if part).strip()
    
    @property
    def years_display(self):
        end_year = self.death_date.year if self.death_date else "?"
        return f"({self.birth_date.year}-{end_year})"
