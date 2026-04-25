from django.urls import path

from .views import (
    GroupCreateView,
    GroupDetailView,
    GroupListView,
    LessonCreateView,
    LessonDeleteView,
    LessonUpdateView,
    VideoLessonCreateView,
)

app_name = "courses"

urlpatterns = [
    path("groups/", GroupListView.as_view(), name="group_list"),
    path("groups/new/", GroupCreateView.as_view(), name="group_create"),
    path("groups/<int:pk>/", GroupDetailView.as_view(), name="group_detail"),
    path("groups/<int:pk>/lessons/new/", LessonCreateView.as_view(), name="lesson_create"),
    path("videos/new/", VideoLessonCreateView.as_view(), name="video_lesson_create"),
    path("lessons/<int:pk>/edit/", LessonUpdateView.as_view(), name="lesson_edit"),
    path("lessons/<int:pk>/delete/", LessonDeleteView.as_view(), name="lesson_delete"),
]
