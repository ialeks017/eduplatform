from django import forms
from django.contrib.auth import get_user_model

from .models import Lesson, StudyGroup


class StudyGroupForm(forms.ModelForm):
    class Meta:
        model = StudyGroup
        fields = ["name", "description", "students"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        User = get_user_model()
        self.fields["students"].queryset = User.objects.filter(role="student")
        self.fields["students"].required = False


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ["subject", "duration_minutes", "cost", "description", "homework"]
