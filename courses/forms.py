from django import forms
from django.contrib.auth import get_user_model

from .models import Lesson, StudyGroup, VideoLesson


class StudyGroupForm(forms.ModelForm):
    class Meta:
        model = StudyGroup
        fields = ["name", "description", "teachers", "students"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        User = get_user_model()
        self.fields["teachers"].queryset = User.objects.filter(role="teacher")
        self.fields["teachers"].required = False
        self.fields["students"].queryset = User.objects.filter(role="student")
        self.fields["students"].required = False


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ["subject", "status", "duration_minutes", "cost", "description", "homework"]


class VideoLessonForm(forms.ModelForm):
    class Meta:
        model = VideoLesson
        fields = ["title", "description", "video_file", "groups"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user is None:
            self.fields["groups"].queryset = StudyGroup.objects.none()
            return

        if user.role == "admin":
            self.fields["groups"].queryset = StudyGroup.objects.all()
        elif user.role == "teacher":
            self.fields["groups"].queryset = StudyGroup.objects.filter(teachers=user)
        else:
            self.fields["groups"].queryset = StudyGroup.objects.none()
