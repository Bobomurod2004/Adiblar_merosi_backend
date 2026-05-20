from datetime import timedelta

from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.articles.models import Article
from apps.writers.models import Writer


class ArticleApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='StrongPass123',
        )

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

    def create_article(self, title, *, days_ago=0, status_value='published'):
        published_at = timezone.now() - timedelta(days=days_ago)
        return Article.objects.create(
            title=title,
            author=self.user,
            writer=self.writer,
            summary=f'{title} uchun qisqa tavsif',
            content=f'{title} uchun to‘liq matn',
            status=status_value,
            published_at=published_at if status_value == 'published' else None,
        )

    def test_home_articles_returns_latest_three_published(self):
        self.create_article('Maqola 4', days_ago=4)
        a3 = self.create_article('Maqola 3', days_ago=3)
        a2 = self.create_article('Maqola 2', days_ago=2)
        a1 = self.create_article('Maqola 1', days_ago=1)
        self.create_article('Maqola Draft', status_value='draft')

        response = self.client.get(reverse('articles:article-home-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 3)

        returned_ids = [item['id'] for item in response.data]
        self.assertEqual(returned_ids, [a1.id, a2.id, a3.id])

    def test_article_detail_increments_views_count(self):
        article = self.create_article('Ko‘riladigan maqola', days_ago=0)
        detail_url = reverse('articles:article-detail', kwargs={'slug': article.slug})

        self.assertEqual(article.views_count, 0)

        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        article.refresh_from_db()
        self.assertEqual(article.views_count, 1)

    def test_article_detail_does_not_double_increment_in_same_session(self):
        article = self.create_article('Double increment testi', days_ago=0)
        detail_url = reverse('articles:article-detail', kwargs={'slug': article.slug})

        first = self.client.get(detail_url)
        second = self.client.get(detail_url)

        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertEqual(second.status_code, status.HTTP_200_OK)

        article.refresh_from_db()
        self.assertEqual(article.views_count, 1)

    def test_missing_article_media_urls_return_null(self):
        article = self.create_article('Media yo‘q maqola', days_ago=0)
        article.featured_image = 'articles/images/missing.jpg'
        article.article_file = 'articles/files/missing.pdf'
        article.save(update_fields=['featured_image', 'article_file'])

        list_response = self.client.get(reverse('articles:article-list'))
        detail_response = self.client.get(reverse('articles:article-detail', kwargs={'slug': article.slug}))

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)

        list_item = next(item for item in list_response.data['results'] if item['id'] == article.id)
        self.assertIsNone(list_item['featured_image'])
        self.assertIsNone(list_item['article_file'])
        self.assertIsNone(detail_response.data['featured_image'])
        self.assertIsNone(detail_response.data['article_file'])
