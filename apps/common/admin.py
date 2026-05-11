from django.contrib import admin
from unfold.admin import ModelAdmin, StackedInline, TabularInline

from .models import (
    PracticeOption,
    PracticeQuestion,
    PracticeTest,
    ScholarshipApplication,
    ScholarshipProgram,
    TestAttempt,
)


class PracticeOptionInline(TabularInline):
    model = PracticeOption
    extra = 4
    min_num = 2
    validate_min = True
    fields = ('order', 'option_text', 'is_correct')
    ordering = ('order',)
    classes = ('tab',)


class PracticeQuestionInline(StackedInline):
    model = PracticeQuestion
    extra = 1
    fields = ('order', 'prompt', 'explanation')
    ordering = ('order',)
    inlines = [PracticeOptionInline]
    classes = ('tab',)


class ScholarshipProgramAdmin(ModelAdmin):
    list_display = ('name', 'monthly_amount', 'deadline', 'is_open', 'is_active')
    list_filter = ('is_active', 'is_open', 'deadline')
    search_fields = ('name', 'description')
    readonly_fields = ('slug', 'created_at', 'updated_at')


class ScholarshipApplicationAdmin(ModelAdmin):
    list_display = ('full_name', 'program', 'status', 'university', 'created_at')
    list_filter = ('status', 'program', 'created_at')
    search_fields = ('full_name', 'email', 'university', 'applicant__username')
    readonly_fields = ('applicant', 'program', 'created_at', 'updated_at')


class PracticeTestAdmin(ModelAdmin):
    list_display = ('title', 'topic', 'level', 'duration_minutes', 'pass_percent', 'is_active')
    list_filter = ('level', 'is_active')
    search_fields = ('title', 'topic', 'description')
    readonly_fields = ('slug', 'created_at', 'updated_at')
    fieldsets = (
        ('Asosiy ma’lumotlar', {'fields': ('title', 'slug', 'topic', 'description')}),
        ('Test sozlamalari', {'fields': ('duration_minutes', 'level', 'pass_percent', 'is_active')}),
        ('Vaqt oralig‘i', {'fields': ('starts_at', 'expires_at')}),
        ('Tizim', {'fields': ('created_at', 'updated_at')}),
    )
    inlines = [PracticeQuestionInline]


class PracticeQuestionAdmin(ModelAdmin):
    list_display = ('test', 'order')
    list_filter = ('test',)
    search_fields = ('prompt',)
    inlines = [PracticeOptionInline]


class PracticeOptionAdmin(ModelAdmin):
    list_display = ('question', 'order', 'is_correct')
    list_filter = ('is_correct', 'question__test')
    search_fields = ('option_text', 'question__prompt')


class TestAttemptAdmin(ModelAdmin):
    list_display = ('test', 'user', 'score_percent', 'correct_answers', 'total_questions', 'created_at')
    list_filter = ('test', 'created_at')
    search_fields = ('user__username', 'test__title')
    readonly_fields = (
        'test',
        'user',
        'total_questions',
        'correct_answers',
        'score_percent',
        'time_spent_seconds',
        'answers_data',
        'created_at',
        'updated_at',
    )


for model, model_admin in [
    (ScholarshipProgram, ScholarshipProgramAdmin),
    (ScholarshipApplication, ScholarshipApplicationAdmin),
    (PracticeTest, PracticeTestAdmin),
    (PracticeQuestion, PracticeQuestionAdmin),
    (PracticeOption, PracticeOptionAdmin),
    (TestAttempt, TestAttemptAdmin),
]:
    if model not in admin.site._registry:
        admin.site.register(model, model_admin)
