from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    UserRegisterView, UserProfileView, UserProfileUpdateView,
    BookmarkListView, BookmarkCreateView, BookmarkDeleteView,
    MyTokenObtainPairView
)

app_name = 'users'

urlpatterns = [
    # Authentication
    path('auth/register/', UserRegisterView.as_view(), name='register'),
    path('auth/login/', MyTokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # User Profile
    path('me/', UserProfileView.as_view(), name='user-profile'),
    path('me/update/', UserProfileUpdateView.as_view(), name='user-profile-update'),
    
    # Bookmarks
    path('me/bookmarks/', BookmarkListView.as_view(), name='bookmark-list'),
    path('bookmarks/create/', BookmarkCreateView.as_view(), name='bookmark-create'),
    path('bookmarks/<int:id>/delete/', BookmarkDeleteView.as_view(), name='bookmark-delete'),
]
