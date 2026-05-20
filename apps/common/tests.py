import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.writers.models import Writer
from apps.works.models import LiteraryGenre, LiteraryWork
from .models import (
    PracticeOption,
    PracticeQuestion,
    PracticeTest,
    ScholarshipApplication,
    ScholarshipProgram,
)
from .media import safe_media_url
from .media_views import serve_media_file

User = get_user_model()


class CommonEndpointsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='StrongPass123',
        )

        self.scholarship = ScholarshipProgram.objects.create(
            name='Muqimiy stipendiyasi',
            description='Test stipendiya tavsifi',
            monthly_amount='2500000.00',
            requirements='Talab 1\nTalab 2',
            deadline='2026-09-15',
            is_active=True,
            is_open=True,
        )

        self.practice_test = PracticeTest.objects.create(
            title="Muqimiy bo'yicha test",
            topic='Biografiya va ijod',
            description='Demo test',
            duration_minutes=20,
            level='intermediate',
            pass_percent=60,
            is_active=True,
        )

        question = PracticeQuestion.objects.create(
            test=self.practice_test,
            prompt="Muqimiyning tug'ilgan yili qaysi?",
            order=1,
        )
        self.correct_option = PracticeOption.objects.create(
            question=question,
            option_text='1850',
            is_correct=True,
            order=1,
        )
        PracticeOption.objects.create(
            question=question,
            option_text='1907',
            is_correct=False,
            order=2,
        )

    def test_scholarship_list_returns_data(self):
        response = self.client.get('/api/v1/meta/scholarships/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertGreater(len(response.data['results']), 0)

    def test_scholarship_apply_requires_auth(self):
        response = self.client.post(
            f'/api/v1/meta/scholarships/{self.scholarship.slug}/apply/',
            {
                'full_name': 'Ali Valiyev',
                'email': 'ali@example.com',
                'university': 'TATU',
                'motivation_letter': 'Men stipendiyaga ariza topshiraman.',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_scholarship_apply_success_and_duplicate_block(self):
        self.client.force_authenticate(user=self.user)

        payload = {
            'full_name': 'Ali Valiyev',
            'email': 'ali@example.com',
            'phone': '+998901112233',
            'university': 'TATU',
            'study_year': '3-kurs',
            'gpa': '3.80',
            'motivation_letter': 'Men stipendiyaga ariza topshiraman.',
            'portfolio_url': 'https://example.com/portfolio',
        }

        first_response = self.client.post(
            f'/api/v1/meta/scholarships/{self.scholarship.slug}/apply/',
            payload,
            format='json',
        )
        second_response = self.client.post(
            f'/api/v1/meta/scholarships/{self.scholarship.slug}/apply/',
            payload,
            format='json',
        )

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ScholarshipApplication.objects.count(), 1)

    def test_test_detail_and_submit(self):
        detail_response = self.client.get(f'/api/v1/meta/tests/{self.practice_test.slug}/')
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.data['slug'], self.practice_test.slug)

        first_question = detail_response.data['questions'][0]
        self.assertIn('options', first_question)
        self.assertNotIn('is_correct', first_question['options'][0])

        submit_response = self.client.post(
            f'/api/v1/meta/tests/{self.practice_test.slug}/submit/',
            {
                'answers': {str(first_question['id']): self.correct_option.id},
                'time_spent_seconds': 32,
            },
            format='json',
        )

        self.assertEqual(submit_response.status_code, status.HTTP_200_OK)
        self.assertTrue(submit_response.data['passed'])
        self.assertEqual(submit_response.data['correct_answers'], 1)

    def test_ai_chat_requires_message(self):
        response = self.client.post('/api/v1/meta/ai-chat/', {'message': ''}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ai_chat_returns_answer(self):
        response = self.client.post(
            '/api/v1/meta/ai-chat/',
            {'message': 'Muqimiy ijodi haqida aytib bering'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('Muqimiy', response.data['message'])


class MediaCompatibilityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.writer = Writer.objects.create(
            first_name='Abdulla',
            last_name='Qahhor',
            short_bio='Qisqa bio',
            detailed_bio='Batafsil bio',
            birth_date='1907-09-17',
            birth_place="Qo'qon",
            main_genres='Hikoya',
        )
        self.genre = LiteraryGenre.objects.create(name='Roman', slug='roman')
        self.work = LiteraryWork.objects.create(
            title='Anor',
            writer=self.writer,
            genre=self.genre,
            description='Test tavsif',
            content='Test matn',
            publication_year=2012,
        )

    @override_settings(MEDIA_URL='/media/')
    def test_safe_media_url_works_with_media_prefixed_name(self):
        with tempfile.TemporaryDirectory() as media_root:
            cover_path = Path(media_root) / 'works' / 'covers' / 'anor.webp'
            cover_path.parent.mkdir(parents=True, exist_ok=True)
            cover_path.write_bytes(b'anor-image')

            self.work.cover_image = '/media/works/covers/anor.webp'
            self.work.save(update_fields=['cover_image'])

            with override_settings(MEDIA_ROOT=media_root):
                url = safe_media_url(self.work.cover_image)

            self.assertEqual(url, '/media/works/covers/anor.webp')

    @override_settings(MEDIA_URL='/media/')
    def test_safe_media_url_and_media_view_use_fallback_root(self):
        with tempfile.TemporaryDirectory() as primary_media_root, tempfile.TemporaryDirectory() as fallback_media_root:
            cover_path = Path(fallback_media_root) / 'works' / 'covers' / 'legacy.webp'
            cover_path.parent.mkdir(parents=True, exist_ok=True)
            cover_path.write_bytes(b'legacy-image')

            self.work.cover_image = 'works/covers/legacy.webp'
            self.work.save(update_fields=['cover_image'])

            with patch.dict(os.environ, {'MEDIA_ROOT_FALLBACKS': fallback_media_root}, clear=False):
                with override_settings(MEDIA_ROOT=primary_media_root):
                    url = safe_media_url(self.work.cover_image)
                    response = serve_media_file(self.factory.get('/media/works/covers/legacy.webp'), 'works/covers/legacy.webp')
                    content = b''.join(response.streaming_content)

            self.assertEqual(url, '/media/works/covers/legacy.webp')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(content, b'legacy-image')
