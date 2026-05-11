from apps.articles.models import Article
from apps.common.models import PracticeTest, ScholarshipApplication, ScholarshipProgram
from apps.users.models import UserProfile
from apps.works.models import LiteraryWork
from apps.writers.models import Writer


def dashboard_callback(request, context):
    """Unfold dashboard uchun asosiy statistik bloklar."""
    published_articles = Article.objects.filter(status='published').count()
    pending_articles = Article.objects.filter(status='pending').count()
    submitted_applications = ScholarshipApplication.objects.filter(status='submitted').count()

    context.update(
        {
            "stats": [
                {
                    "title": "Yozuvchilar",
                    "value": Writer.objects.count(),
                    "description": "Platformadagi faol adiblar soni",
                },
                {
                    "title": "Asarlar",
                    "value": LiteraryWork.objects.count(),
                    "description": "Kutubxonadagi adabiy asarlar",
                },
                {
                    "title": "E'lon qilingan maqolalar",
                    "value": published_articles,
                    "description": "Ochiq bazadagi maqolalar soni",
                },
                {
                    "title": "Kutilayotgan maqolalar",
                    "value": pending_articles,
                    "description": "Moderatsiyani kutayotgan materiallar",
                },
                {
                    "title": "Testlar",
                    "value": PracticeTest.objects.count(),
                    "description": "Platformadagi test to'plamlari",
                },
                {
                    "title": "Stipendiya arizalari",
                    "value": submitted_applications,
                    "description": "Ko'rib chiqilishini kutayotgan arizalar",
                },
            ],
            "quick_links": [
                {
                    "title": "Yangi yozuvchi qo'shish",
                    "link": "/admin/writers/writer/add/",
                },
                {
                    "title": "Yangi asar qo'shish",
                    "link": "/admin/works/literarywork/add/",
                },
                {
                    "title": "Kutilayotgan maqolalar",
                    "link": "/admin/articles/article/?status__exact=pending",
                },
                {
                    "title": "Foydalanuvchilar",
                    "link": "/admin/auth/user/",
                },
                {
                    "title": "Stipendiya dasturlari",
                    "link": "/admin/common/scholarshipprogram/",
                },
                {
                    "title": "Testlar bazasi",
                    "link": "/admin/common/practicetest/",
                },
            ],
            "user_profiles_count": UserProfile.objects.count(),
            "scholarships_count": ScholarshipProgram.objects.count(),
        }
    )

    return context
