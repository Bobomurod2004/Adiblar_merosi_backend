from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import (
    PracticeOption,
    PracticeQuestion,
    PracticeTest,
    ScholarshipApplication,
    ScholarshipProgram,
)

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
