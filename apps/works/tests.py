from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.writers.models import Writer
from .models import LiteraryGenre, LiteraryWork, BookFile


class WorkMediaApiTests(APITestCase):
    def setUp(self):
        self.writer = Writer.objects.create(
            first_name='Abdulla',
            last_name='Qahhor',
            short_bio='Qisqa bio',
            detailed_bio='Batafsil bio',
            birth_date='1907-09-17',
            birth_place='Qo‘qon',
            main_genres='Nasr',
            is_active=True,
        )
        self.genre = LiteraryGenre.objects.create(name='Qissa', slug='qissa')

    def test_missing_cover_and_book_file_urls_return_null(self):
        work = LiteraryWork.objects.create(
            title='Sinov asari',
            writer=self.writer,
            genre=self.genre,
            description='Tavsif',
            introduction='Kirish',
            content='Matn',
            publication_year=2001,
            is_published=True,
            cover_image='works/covers/missing.jpg',
        )
        BookFile.objects.create(
            work=work,
            file_type='pdf',
            file='works/files/missing.pdf',
            file_size=123,
        )

        list_response = self.client.get(reverse('works:work-list'))
        detail_response = self.client.get(reverse('works:work-detail', kwargs={'slug': work.slug}))

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)

        list_item = list_response.data['results'][0]
        self.assertIsNone(list_item['cover_image'])
        self.assertEqual(list_item['has_book_file'], False)
        self.assertIsNone(list_item['book_file_type'])

        self.assertIsNone(detail_response.data['cover_image'])
        self.assertIsNotNone(detail_response.data['book_file'])
        self.assertIsNone(detail_response.data['book_file']['file'])

    def test_work_without_bookfile_relation_serializes_cleanly(self):
        work = LiteraryWork.objects.create(
            title='BookFile yo‘q asar',
            writer=self.writer,
            genre=self.genre,
            description='Tavsif',
            content='Matn',
            publication_year=2002,
            is_published=True,
        )

        response = self.client.get(reverse('works:work-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item = next(obj for obj in response.data['results'] if obj['id'] == work.id)
        self.assertEqual(item['has_book_file'], False)
        self.assertIsNone(item['book_file_type'])
