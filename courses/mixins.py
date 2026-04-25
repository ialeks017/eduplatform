from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .models import Lesson, StudyGroup


class AdminOrTeacherMixin(LoginRequiredMixin):
    """Разрешает доступ администраторам и преподавателям."""

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if request.user.is_authenticated and request.user.role not in ("admin", "teacher"):
            raise PermissionDenied
        return response


class AdminOnlyMixin(LoginRequiredMixin):
    """Разрешает доступ только администраторам."""

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if request.user.is_authenticated and request.user.role != "admin":
            raise PermissionDenied
        return response


class GroupTeacherMixin(AdminOrTeacherMixin):
    """Администратор имеет полный доступ; преподаватель — только к своим группам."""

    def get_group(self):
        if not hasattr(self, "_group"):
            self._group = get_object_or_404(StudyGroup, pk=self.kwargs["pk"])
        return self._group

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if request.user.is_authenticated and request.user.role != "admin":
            if not self.get_group().teachers.filter(pk=request.user.pk).exists():
                raise PermissionDenied
        return response


class LessonOwnerMixin(AdminOrTeacherMixin):
    """Администратор имеет полный доступ; преподаватель — только к занятиям своих групп."""

    def get_lesson(self):
        if not hasattr(self, "_lesson"):
            self._lesson = get_object_or_404(Lesson, pk=self.kwargs["pk"])
        return self._lesson

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if request.user.is_authenticated and request.user.role != "admin":
            if not self.get_lesson().group.teachers.filter(pk=request.user.pk).exists():
                raise PermissionDenied
        return response
