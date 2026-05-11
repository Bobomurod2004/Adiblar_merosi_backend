from django.urls import path

from .views import (
    AIChatView,
    ScholarshipApplyView,
    ScholarshipListView,
    TestDetailView,
    TestListView,
    TestSubmitView,
)

app_name = 'common'

urlpatterns = [
    path('scholarships/', ScholarshipListView.as_view(), name='scholarship-list'),
    path('scholarships/<slug:slug>/apply/', ScholarshipApplyView.as_view(), name='scholarship-apply'),
    path('tests/', TestListView.as_view(), name='test-list'),
    path('tests/<slug:slug>/', TestDetailView.as_view(), name='test-detail'),
    path('tests/<slug:slug>/submit/', TestSubmitView.as_view(), name='test-submit'),
    path('ai-chat/', AIChatView.as_view(), name='ai-chat'),
]
