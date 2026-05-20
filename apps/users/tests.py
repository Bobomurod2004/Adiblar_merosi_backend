from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import UserProfile


class UserProfileMediaTests(APITestCase):
    def test_missing_avatar_url_returns_null(self):
        user = User.objects.create_user(username='profile_user', password='StrongPass123')
        profile = UserProfile.objects.create(user=user, bio='Bio')
        profile.avatar = 'users/avatars/missing.jpg'
        profile.save(update_fields=['avatar'])

        self.client.force_authenticate(user=user)
        response = self.client.get(reverse('users:user-profile'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['avatar'])
