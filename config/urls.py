"""URL configuration for config project."""

from django.contrib import admin
from django.urls import include, path

from users.views import HomeView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomeView.as_view(), name="home"),
    path("", include("users.urls")),
]
