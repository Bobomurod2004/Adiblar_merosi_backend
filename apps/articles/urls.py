from django.urls import path
from .views import (
    ArticleListView, ArticleHomeListView, ArticleDetailView, ArticleCreateView,
    ArticleApproveView, ArticleRejectView, TagListView, UserArticleListView
)

app_name = 'articles'

urlpatterns = [
    # Tags
    path('tags/', TagListView.as_view(), name='tag-list'),
    
    # Articles
    path('home/', ArticleHomeListView.as_view(), name='article-home-list'),
    path('', ArticleListView.as_view(), name='article-list'),
    path('create/', ArticleCreateView.as_view(), name='article-create'),
    path('my-articles/', UserArticleListView.as_view(), name='user-articles'),
    path('<slug:slug>/', ArticleDetailView.as_view(), name='article-detail'),
    
    # Admin actions
    path('<int:id>/approve/', ArticleApproveView.as_view(), name='article-approve'),
    path('<int:id>/reject/', ArticleRejectView.as_view(), name='article-reject'),
]
