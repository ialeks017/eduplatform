from django.urls import path

from .views import (
    AdminStatisticsView,
    GroupCreateView,
    GroupDetailView,
    CalendarView,
    GroupListView,
    LessonCreateView,
    RecurringLessonPlanCreateView,
    LessonDuplicateView,
    LessonDeleteView,
    LessonUpdateView,
    RecurringLessonPlanDeleteView,
    VideoLessonCreateView,
    RecurringLessonPlanUpdateView,
)

app_name = "courses"

urlpatterns = [
    path("calendar/", CalendarView.as_view(), name="calendar"),
    path("groups/", GroupListView.as_view(), name="group_list"),
    path("statistics/", AdminStatisticsView.as_view(), name="statistics"),
    path("groups/new/", GroupCreateView.as_view(), name="group_create"),
    path("groups/<int:pk>/", GroupDetailView.as_view(), name="group_detail"),
    path("groups/<int:pk>/lessons/new/", LessonCreateView.as_view(), name="lesson_create"),
    path("groups/<int:pk>/plans/new/", RecurringLessonPlanCreateView.as_view(), name="plan_create"),
    path("plans/<int:pk>/edit/", RecurringLessonPlanUpdateView.as_view(), name="plan_edit"),
    path("plans/<int:pk>/delete/", RecurringLessonPlanDeleteView.as_view(), name="plan_delete"),
    path("videos/new/", VideoLessonCreateView.as_view(), name="video_lesson_create"),
    path("lessons/<int:pk>/edit/", LessonUpdateView.as_view(), name="lesson_edit"),
    path("lessons/<int:pk>/duplicate/", LessonDuplicateView.as_view(), name="lesson_duplicate"),
    path("lessons/<int:pk>/delete/", LessonDeleteView.as_view(), name="lesson_delete"),
]
