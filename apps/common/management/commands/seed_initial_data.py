from decimal import Decimal
import os

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.writers.models import Writer
from apps.works.models import LiteraryGenre, LiteraryWork, BookFile
from apps.articles.models import Tag, Article
from apps.common.models import (
    PracticeOption,
    PracticeQuestion,
    PracticeTest,
    ScholarshipProgram,
)


User = get_user_model()


class Command(BaseCommand):
    help = 'Muqimiy va Abdulla Qahhor uchun boshlang‘ich seed data yaratadi.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('Seed data yaratish boshlandi...'))

        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@adiblarmerosi.uz',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
            },
        )
        if not admin_user.has_usable_password():
            default_admin_password = os.getenv('SEED_ADMIN_PASSWORD', 'ChangeMe123!')
            admin_user.set_password(default_admin_password)
            admin_user.save(update_fields=['password'])
            self.stdout.write(
                self.style.WARNING(
                    "Admin uchun default parol qo'yildi. Xavfsizlik uchun uni darhol almashtiring."
                )
            )

        prose, _ = LiteraryGenre.objects.get_or_create(
            slug='nasr',
            defaults={
                'name': 'Nasr',
                'description': 'Hikoya, qissa va roman yo‘nalishidagi asarlar.',
            },
        )
        poetry, _ = LiteraryGenre.objects.get_or_create(
            slug='sheriyat',
            defaults={
                'name': 'She\'riyat',
                'description': 'She’riy asarlar to‘plami.',
            },
        )
        criticism, _ = LiteraryGenre.objects.get_or_create(
            slug='tanqid',
            defaults={
                'name': 'Tanqid',
                'description': 'Adabiy tahlil va tanqidiy yo‘nalish.',
            },
        )

        muqimiy, _ = Writer.objects.get_or_create(
            slug='muqimiy',
            defaults={
                'first_name': 'Muqimiy',
                'last_name': '',
                'short_bio': 'Muqimiy o‘zbek adabiyotidagi xalqona ruh va ijtimoiy tanqid bilan mashhur klassik shoir.',
                'detailed_bio': (
                    'Muqimiy o‘z davrining ijtimoiy muammolarini she’riyat orqali yoritgan. '
                    'Uning ijodida ma’rifat, xalq hayoti va tanqidiy kuzatuv markaziy o‘rin tutadi.'
                ),
                'birth_date': '1850-01-01',
                'death_date': '1903-01-01',
                'birth_place': 'Qo‘qon',
                'death_place': 'Qo‘qon',
                'creative_period_start': 1870,
                'creative_period_end': 1903,
                'main_genres': 'She\'riyat, hajv, ma’rifiy asarlar',
                'influenced_by': 'Nodira, Furqat',
                'influenced': 'Keyingi ma’rifatchi shoirlar',
                'legacy': 'Muqimiy xalq tiliga yaqin, mazmunli va teran ijodiy meros qoldirgan.',
            },
        )

        qahhor, _ = Writer.objects.get_or_create(
            slug='abdulla-qahhor',
            defaults={
                'first_name': 'Abdulla',
                'last_name': 'Qahhor',
                'short_bio': 'Abdulla Qahhor o‘zbek nasri va dramaturgiyasining yirik vakillaridan biri.',
                'detailed_bio': (
                    'Abdulla Qahhor hikoya janrini o‘zbek adabiyotida yangi bosqichga olib chiqdi. '
                    'Uning asarlarida inson xarakteri, ijtimoiy munosabat va psixologik chuqurlik kuchli ifodalangan.'
                ),
                'birth_date': '1907-09-17',
                'death_date': '1968-05-25',
                'birth_place': 'Qo‘qon',
                'death_place': 'Toshkent',
                'creative_period_start': 1920,
                'creative_period_end': 1968,
                'main_genres': 'Hikoya, qissa, roman, drama',
                'influenced_by': 'Jadid adabiyoti, realistik maktab',
                'influenced': 'Zamonaviy o‘zbek nasri vakillari',
                'legacy': 'Abdulla Qahhor ixcham, chuqur ma’noli nasr bilan adabiyotda kuchli maktab yaratdi.',
            },
        )

        tags = {}
        for tag_name in ['tanqid', 'biografiya', 'ijod', 'meros', 'maqola']:
            tag, _ = Tag.objects.get_or_create(name=tag_name, defaults={'slug': tag_name})
            tags[tag_name] = tag

        works = [
            {
                'title': 'Muqimiy saylanmasi',
                'writer': muqimiy,
                'genre': poetry,
                'description': 'Muqimiy she’riy merosidan tanlangan namunalar to‘plami.',
                'introduction': 'Bu to‘plam shoir ijodidagi xalqona va ma’rifiy yo‘nalishni ko‘rsatadi.',
                'content': 'Muqimiy she’rlari va hajviy yo‘nalishidagi namunalar.',
                'publication_year': 1905,
                'rating': Decimal('4.80'),
                'is_featured': True,
            },
            {
                'title': 'Tanlangan asarlar',
                'writer': qahhor,
                'genre': prose,
                'description': 'Abdulla Qahhorning eng mashhur hikoya va qissalari jamlanmasi.',
                'introduction': 'O‘zbek nasrining kuchli namunalarini bir joyga jamlaydi.',
                'content': 'Abdulla Qahhor hikoyalari va qissalaridan parchalar.',
                'publication_year': 1969,
                'rating': Decimal('4.90'),
                'is_featured': True,
            },
            {
                'title': 'Adabiy tahlilga kirish',
                'writer': qahhor,
                'genre': criticism,
                'description': 'Qahhor ijodini tahlil qilishga bag‘ishlangan kirish material.',
                'introduction': 'Bu material keyinchalik maqolalar va izohlar bilan boyitiladi.',
                'content': 'Qahhor ijodining uslubiy xususiyatlari.',
                'publication_year': 1970,
                'rating': Decimal('4.60'),
                'is_featured': False,
            },
        ]

        for work_data in works:
            work, created = LiteraryWork.objects.get_or_create(
                title=work_data['title'],
                writer=work_data['writer'],
                defaults={
                    'genre': work_data['genre'],
                    'description': work_data['description'],
                    'introduction': work_data['introduction'],
                    'content': work_data['content'],
                    'publication_year': work_data['publication_year'],
                    'original_language': 'Uzbek',
                    'rating': work_data['rating'],
                    'is_featured': work_data['is_featured'],
                    'is_published': True,
                },
            )

            if created and not BookFile.objects.filter(work=work).exists():
                file_content = f"{work.title}\n\n{work.content}\n"
                filename = f"{work.slug}.txt"
                book_file = BookFile(
                    work=work,
                    file_type='txt',
                    pages_count=1,
                    file_size=len(file_content.encode('utf-8')),
                    language='Uzbek',
                )
                book_file.file.save(filename, ContentFile(file_content), save=False)
                book_file.save()

        published_articles = [
            {
                'title': 'Muqimiy ijodida xalq tili va ma’rifat',
                'author': admin_user,
                'writer': muqimiy,
                'summary': 'Muqimiy asarlarida xalq ruhiyati va ma’rifiy g‘oyalar qanday uyg‘unlashgani haqida.',
                'content': 'Muqimiy ijodi yuzasidan qisqa tahliliy maqola.',
                'tags': [tags['tanqid'], tags['ijod'], tags['meros']],
            },
            {
                'title': 'Abdulla Qahhor nasrida ixchamlik san’ati',
                'author': admin_user,
                'writer': qahhor,
                'summary': 'Qahhor hikoyalaridagi ixcham forma va mazmun zichligi haqida tahlil.',
                'content': 'Abdulla Qahhor nasri tahliliga bag‘ishlangan maqola.',
                'tags': [tags['tanqid'], tags['ijod']],
            },
        ]

        for article_data in published_articles:
            article, created = Article.objects.get_or_create(
                title=article_data['title'],
                author=article_data['author'],
                defaults={
                    'writer': article_data['writer'],
                    'summary': article_data['summary'],
                    'content': article_data['content'],
                    'status': 'published',
                    'submitted_at': timezone.now(),
                    'published_at': timezone.now(),
                },
            )
            if created:
                article.tags.set(article_data['tags'])

        pending_article, created = Article.objects.get_or_create(
            title='Foydalanuvchi maqolasi namunasi',
            author=admin_user,
            defaults={
                'writer': qahhor,
                'summary': 'Admin tasdiqlashini kutayotgan maqola namunasi.',
                'content': 'Bu maqola moderatsiya jarayonini ko‘rsatish uchun yaratilgan.',
                'status': 'pending',
                'submitted_at': timezone.now(),
            },
        )
        if created:
            pending_article.tags.set([tags['maqola']])

        scholarship_programs = [
            {
                'name': 'Muqimiy stipendiyasi',
                'slug': 'muqimiy-stipendiyasi',
                'description': 'Adabiyot yo‘nalishida yuqori natija ko‘rsatgan bakalavr talabalar uchun dastur.',
                'monthly_amount': Decimal('2500000.00'),
                'requirements': (
                    "Kamida 3.5 GPA yoki tenglashtirilgan yuqori o'zlashtirish\n"
                    "Adabiyot bo'yicha ilmiy maqola yoki loyiha\n"
                    "Tavsiyanoma va motivatsion xat"
                ),
                'deadline': '2026-09-15',
            },
            {
                'name': 'Abdulla Qahhor stipendiyasi',
                'slug': 'abdulla-qahhor-stipendiyasi',
                'description': 'Yosh ijodkorlar va ilmiy izlanish olib borayotgan magistratura talabalari uchun maxsus grant.',
                'monthly_amount': Decimal('3000000.00'),
                'requirements': (
                    "Yaratilgan ijodiy ishlar portfeli\n"
                    "Adabiy tanqid yoki tahliliy maqola tajribasi\n"
                    "Suhbat bosqichidan muvaffaqiyatli o'tish"
                ),
                'deadline': '2026-10-01',
            },
        ]

        for program_data in scholarship_programs:
            ScholarshipProgram.objects.get_or_create(
                slug=program_data['slug'],
                defaults={
                    'name': program_data['name'],
                    'description': program_data['description'],
                    'monthly_amount': program_data['monthly_amount'],
                    'requirements': program_data['requirements'],
                    'deadline': program_data['deadline'],
                    'is_active': True,
                    'is_open': True,
                },
            )

        tests_data = [
            {
                'title': "Abdulla Qahhor bo'yicha test",
                'slug': 'abdulla-qahhor-boyicha-test',
                'topic': 'Biografiya va asarlar',
                'description': 'Abdulla Qahhor hayoti va ijodi bo‘yicha asosiy bilimlarni tekshiradi.',
                'duration_minutes': 25,
                'level': 'intermediate',
                'pass_percent': 60,
                'questions': [
                    {
                        'prompt': "Abdulla Qahhor qaysi yili tug'ilgan?",
                        'options': [
                            ("1907", True),
                            ("1850", False),
                            ("1915", False),
                            ("1899", False),
                        ],
                    },
                    {
                        'prompt': "Abdulla Qahhor asarlarida ko'proq qaysi janr kuchli?",
                        'options': [
                            ("Hikoya va nasr", True),
                            ("Epos", False),
                            ("Ilmiy fantastika", False),
                            ("Sarguzasht roman", False),
                        ],
                    },
                    {
                        'prompt': "Qahhor ijodidagi asosiy uslubiy belgi qaysi?",
                        'options': [
                            ("Ixchamlik va psixologik chuqurlik", True),
                            ("Faqat she'riy tajriba", False),
                            ("Faqat tarixiy drama", False),
                            ("Diniy risolalar uslubi", False),
                        ],
                    },
                ],
            },
            {
                'title': "Muqimiy bo'yicha test",
                'slug': 'muqimiy-boyicha-test',
                'topic': "Biografiya va she'riyat",
                'description': 'Muqimiy hayoti va she’riy merosi bo‘yicha nazorat testi.',
                'duration_minutes': 25,
                'level': 'intermediate',
                'pass_percent': 60,
                'questions': [
                    {
                        'prompt': "Muqimiy qaysi yillarda yashagan?",
                        'options': [
                            ("1850-1903", True),
                            ("1907-1968", False),
                            ("1830-1899", False),
                            ("1865-1931", False),
                        ],
                    },
                    {
                        'prompt': "Muqimiy ijodida qaysi yo'nalish kuchli ko'rinadi?",
                        'options': [
                            ("Xalqona ruh va ijtimoiy tanqid", True),
                            ("Texnik ilmiy esse", False),
                            ("Faqat tarjima adabiyoti", False),
                            ("Faqat detektiv roman", False),
                        ],
                    },
                    {
                        'prompt': "Muqimiy adabiyotda nimasi bilan mashhur?",
                        'options': [
                            ("Ma'rifatparvar va teran she'riyati bilan", True),
                            ("Astronomik qo'llanmalar yozgani bilan", False),
                            ("Opera bastakorligi bilan", False),
                            ("Faqat siyosiy manifestlari bilan", False),
                        ],
                    },
                ],
            },
        ]

        for test_data in tests_data:
            practice_test, _ = PracticeTest.objects.get_or_create(
                slug=test_data['slug'],
                defaults={
                    'title': test_data['title'],
                    'topic': test_data['topic'],
                    'description': test_data['description'],
                    'duration_minutes': test_data['duration_minutes'],
                    'level': test_data['level'],
                    'pass_percent': test_data['pass_percent'],
                    'is_active': True,
                },
            )

            if practice_test.questions.exists():
                continue

            for question_index, question_data in enumerate(test_data['questions'], start=1):
                question = PracticeQuestion.objects.create(
                    test=practice_test,
                    prompt=question_data['prompt'],
                    order=question_index,
                )

                for option_index, (option_text, is_correct) in enumerate(question_data['options'], start=1):
                    PracticeOption.objects.create(
                        question=question,
                        option_text=option_text,
                        is_correct=is_correct,
                        order=option_index,
                    )

        self.stdout.write(self.style.SUCCESS('Seed data tayyorlandi.'))
        self.stdout.write(self.style.SUCCESS(f'Yozuvchilar: {Writer.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Asarlar: {LiteraryWork.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Maqolalar: {Article.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Stipendiyalar: {ScholarshipProgram.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Testlar: {PracticeTest.objects.count()}'))
