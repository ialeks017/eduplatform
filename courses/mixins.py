from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .models import StudyGroup


class TeacherRequiredMixin(LoginRequiredMixin):
    """Разрешает доступ только пользователям с ролью TEACHER."""

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if request.user.is_authenticated and request.user.role != "teacher":
            raise PermissionDenied
        return response


class GroupTeacherMixin(TeacherRequiredMixin):
    """Дополнительно проверяет, что текущий пользователь — преподаватель этой группы."""

    def get_group(self):
        if not hasattr(self, "_group"):
            self._group = get_object_or_404(StudyGroup, pk=self.kwargs["pk"])
        return self._group

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if request.user.is_authenticated and self.get_group().teacher != request.user:
            raise PermissionDenied
        return response
