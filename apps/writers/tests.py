import tempfile
from io import BytesIO
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from PIL import Image
from .models import Writer


def build_test_image(name='writer.png'):
    buffer = BytesIO()
    Image.new('RGB', (5, 5), (255, 100, 10)).save(buffer, format='PNG')
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/png')


class WriterModelTests(TestCase):
    def test_duplicate_names_generate_unique_slug(self):
        writer1 = Writer.objects.create(
            first_name='Abdulla',
            last_name='Qahhor',
            short_bio='Bio',
            detailed_bio='Detail',
            birth_date='1907-09-17',
            birth_place='Qo‘qon',
            main_genres='Nasr',
        )

        writer2 = Writer.objects.create(
            first_name='Abdulla',
            last_name='Qahhor',
            short_bio='Bio 2',
            detailed_bio='Detail 2',
            birth_date='1908-01-01',
            birth_place='Toshkent',
            main_genres='Nasr',
        )

        self.assertEqual(writer1.slug, 'abdulla-qahhor')
        self.assertEqual(writer2.slug, 'abdulla-qahhor-2')


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class WriterUploadApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/api/v1/writers/'
        self.user_model = get_user_model()

    def _payload(self, first_name='Yozuvchi', last_name='Test'):
        return {
            'first_name': first_name,
            'last_name': last_name,
            'short_bio': 'Qisqa bio',
            'detailed_bio': 'Batafsil bio',
            'birth_date': '1900-01-01',
            'birth_place': 'Toshkent',
            'main_genres': 'Nasr',
            'image': build_test_image(),
        }

    def test_staff_can_upload_writer_image(self):
        staff = self.user_model.objects.create_user(
            username='staff',
            password='StrongPass123!',
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_authenticate(user=staff)

        response = self.client.post(self.url, self._payload(), format='multipart', HTTP_HOST='localhost')

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data['image'].endswith('.png'))
        self.assertEqual(response.data['is_active'], True)
        self.assertEqual(Writer.objects.count(), 1)

    def test_non_staff_cannot_upload_writer_image(self):
        user = self.user_model.objects.create_user(
            username='ordinary',
            password='StrongPass123!',
            is_staff=False,
        )
        self.client.force_authenticate(user=user)

        response = self.client.post(self.url, self._payload('Oddiy', 'Foydalanuvchi'), format='multipart', HTTP_HOST='localhost')

        self.assertEqual(response.status_code, 403)
