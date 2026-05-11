from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify


class BaseModel(models.Model):
    """
    Baza model - Barcha modellar uchun Common fieldlar
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Oʻzgartirilgan vaqti")
    
    class Meta:
        abstract = True
        ordering = ['-created_at']


User = get_user_model()


class ScholarshipProgram(BaseModel):
    """Stipendiya dasturi."""

    name = models.CharField(max_length=255, verbose_name="Nomi")
    slug = models.SlugField(unique=True, blank=True, verbose_name="Slug")
    description = models.TextField(verbose_name="Tavsif")
    monthly_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Oylik miqdori",
    )
    requirements = models.TextField(
        help_text="Har bir talabni yangi qatordan yozing",
        verbose_name="Talablar",
    )
    deadline = models.DateField(verbose_name="Ariza muddati")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    is_open = models.BooleanField(default=True, verbose_name="Qabul ochiq")

    class Meta:
        verbose_name = "Stipendiya dasturi"
        verbose_name_plural = "Stipendiya dasturlari"
        ordering = ['deadline', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'is_open']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def requirements_list(self):
        return [item.strip() for item in self.requirements.splitlines() if item.strip()]


class ScholarshipApplication(BaseModel):
    """Stipendiya arizalari."""

    STATUS_CHOICES = [
        ('submitted', 'Yuborilgan'),
        ('reviewing', "Ko'rib chiqilmoqda"),
        ('accepted', 'Qabul qilingan'),
        ('rejected', 'Rad etilgan'),
    ]

    program = models.ForeignKey(
        ScholarshipProgram,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name="Dastur",
    )
    applicant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='scholarship_applications',
        verbose_name="Arizachi",
    )

    full_name = models.CharField(max_length=255, verbose_name="To'liq ism")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=30, blank=True, verbose_name="Telefon")
    university = models.CharField(max_length=255, verbose_name="Universitet")
    study_year = models.CharField(max_length=50, blank=True, verbose_name="Kurs")
    gpa = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name="GPA",
    )
    motivation_letter = models.TextField(verbose_name="Motivatsion xat")
    portfolio_url = models.URLField(blank=True, verbose_name="Portfolio havolasi")

    status = models.CharField(
        max_length=12,
        choices=STATUS_CHOICES,
        default='submitted',
        verbose_name="Holat",
    )
    admin_notes = models.TextField(blank=True, verbose_name="Admin izohi")
    decided_at = models.DateTimeField(null=True, blank=True, verbose_name="Qaror vaqti")

    class Meta:
        verbose_name = "Stipendiya arizasi"
        verbose_name_plural = "Stipendiya arizalari"
        ordering = ['-created_at']
        unique_together = ('program', 'applicant')
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['program', 'status']),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.program.name}"


class PracticeTest(BaseModel):
    """Test to'plami."""

    LEVEL_CHOICES = [
        ('beginner', "Boshlang'ich"),
        ('intermediate', "O'rta"),
        ('advanced', 'Murakkab'),
    ]

    title = models.CharField(max_length=255, verbose_name="Sarlavha")
    slug = models.SlugField(unique=True, blank=True, verbose_name="Slug")
    topic = models.CharField(max_length=255, verbose_name="Mavzu")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    duration_minutes = models.PositiveSmallIntegerField(default=25, verbose_name="Davomiyligi (daq)")
    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default='intermediate',
        verbose_name="Daraja",
    )
    pass_percent = models.PositiveSmallIntegerField(
        default=60,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name="O'tish foizi",
    )
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    starts_at = models.DateTimeField(null=True, blank=True, verbose_name="Boshlanish vaqti")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Tugash vaqti")

    class Meta:
        verbose_name = "Test"
        verbose_name_plural = "Testlar"
        ordering = ['title']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
            models.Index(fields=['starts_at']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class PracticeQuestion(BaseModel):
    """Test savoli."""

    test = models.ForeignKey(
        PracticeTest,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name="Test",
    )
    prompt = models.TextField(verbose_name="Savol matni")
    explanation = models.TextField(blank=True, verbose_name="Izoh")
    order = models.PositiveIntegerField(default=1, verbose_name="Tartib")

    class Meta:
        verbose_name = "Test savoli"
        verbose_name_plural = "Test savollari"
        ordering = ['order', 'id']
        unique_together = ('test', 'order')
        indexes = [
            models.Index(fields=['test', 'order']),
        ]

    def __str__(self):
        return f"{self.test.title} - Savol {self.order}"


class PracticeOption(BaseModel):
    """Savol variantlari."""

    question = models.ForeignKey(
        PracticeQuestion,
        on_delete=models.CASCADE,
        related_name='options',
        verbose_name="Savol",
    )
    option_text = models.CharField(max_length=500, verbose_name="Variant matni")
    is_correct = models.BooleanField(default=False, verbose_name="To'g'ri javob")
    order = models.PositiveIntegerField(default=1, verbose_name="Tartib")

    class Meta:
        verbose_name = "Savol varianti"
        verbose_name_plural = "Savol variantlari"
        ordering = ['order', 'id']
        unique_together = ('question', 'order')
        indexes = [
            models.Index(fields=['question', 'order']),
        ]

    def __str__(self):
        return f"{self.question} - Variant {self.order}"


class TestAttempt(BaseModel):
    """Test topshirish natijasi."""

    test = models.ForeignKey(
        PracticeTest,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name="Test",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='test_attempts',
        verbose_name="Foydalanuvchi",
    )
    total_questions = models.PositiveIntegerField(default=0, verbose_name="Jami savol")
    correct_answers = models.PositiveIntegerField(default=0, verbose_name="To'g'ri javoblar")
    score_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Foiz natijasi",
    )
    time_spent_seconds = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Sarflangan vaqt (sek)",
    )
    answers_data = models.JSONField(default=dict, blank=True, verbose_name="Javoblar")

    class Meta:
        verbose_name = "Test natijasi"
        verbose_name_plural = "Test natijalari"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['test']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        username = self.user.username if self.user else 'guest'
        return f"{self.test.title} - {username} - {self.score_percent}%"
