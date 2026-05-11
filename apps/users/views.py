from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import UserProfile, Bookmark
from .serializers import (
	UserRegisterSerializer, UserProfileSerializer, BookmarkSerializer,
	MyTokenObtainPairSerializer
)


class MyTokenObtainPairView(TokenObtainPairView):
	serializer_class = MyTokenObtainPairSerializer


class UserRegisterView(generics.CreateAPIView):
	queryset = User.objects.all()
	serializer_class = UserRegisterSerializer
	permission_classes = [AllowAny]


class UserProfileView(generics.RetrieveAPIView):
	serializer_class = UserProfileSerializer
	permission_classes = [IsAuthenticated]

	def get_object(self):
		profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
		return profile


class UserProfileUpdateView(generics.UpdateAPIView):
	serializer_class = UserProfileSerializer
	permission_classes = [IsAuthenticated]

	def get_object(self):
		profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
		return profile


class BookmarkListView(generics.ListAPIView):
	serializer_class = BookmarkSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		return Bookmark.objects.filter(user=self.request.user).select_related('work', 'work__writer')


class BookmarkCreateView(generics.CreateAPIView):
	serializer_class = BookmarkSerializer
	permission_classes = [IsAuthenticated]

	def perform_create(self, serializer):
		serializer.save(user=self.request.user)


class BookmarkDeleteView(generics.DestroyAPIView):
	serializer_class = BookmarkSerializer
	permission_classes = [IsAuthenticated]
	lookup_field = 'id'

	def get_queryset(self):
		return Bookmark.objects.filter(user=self.request.user)
