from django.urls import path

from .views import GroupCreateView, GroupDetailView, GroupListView, LessonCreateView

app_name = "courses"

urlpatterns = [
    path("groups/", GroupListView.as_view(), name="group_list"),
    path("groups/new/", GroupCreateView.as_view(), name="group_create"),
    path("groups/<int:pk>/", GroupDetailView.as_view(), name="group_detail"),
    path("groups/<int:pk>/lessons/new/", LessonCreateView.as_view(), name="lesson_create"),
]
