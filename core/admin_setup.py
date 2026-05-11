from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from django.contrib.auth.admin import GroupAdmin as DjangoGroupAdmin, UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group, User

from apps.articles.admin import ArticleAdmin, ArticleCommentAdmin, TagAdmin
from apps.articles.models import Article, ArticleComment, Tag
from apps.common.admin import (
    PracticeOptionAdmin,
    PracticeQuestionAdmin,
    PracticeTestAdmin,
    ScholarshipApplicationAdmin,
    ScholarshipProgramAdmin,
    TestAttemptAdmin,
)
from apps.common.models import (
    PracticeOption,
    PracticeQuestion,
    PracticeTest,
    ScholarshipApplication,
    ScholarshipProgram,
    TestAttempt,
)
from apps.users.admin import BookmarkAdmin, UserProfileAdmin
from apps.users.models import Bookmark, UserProfile
from apps.works.admin import BookFileAdmin, LiteraryGenreAdmin, LiteraryWorkAdmin
from apps.works.models import BookFile, LiteraryGenre, LiteraryWork
from apps.writers.admin import WriterAdmin
from apps.writers.models import Writer


def register(model, model_admin):
    try:
        admin.site.register(model, model_admin)
    except AlreadyRegistered:
        pass


register(Writer, WriterAdmin)
register(LiteraryGenre, LiteraryGenreAdmin)
register(LiteraryWork, LiteraryWorkAdmin)
register(BookFile, BookFileAdmin)
register(Tag, TagAdmin)
register(Article, ArticleAdmin)
register(ArticleComment, ArticleCommentAdmin)
register(UserProfile, UserProfileAdmin)
register(Bookmark, BookmarkAdmin)
register(ScholarshipProgram, ScholarshipProgramAdmin)
register(ScholarshipApplication, ScholarshipApplicationAdmin)
register(PracticeTest, PracticeTestAdmin)
register(PracticeQuestion, PracticeQuestionAdmin)
register(PracticeOption, PracticeOptionAdmin)
register(TestAttempt, TestAttemptAdmin)
register(User, DjangoUserAdmin)
register(Group, DjangoGroupAdmin)
