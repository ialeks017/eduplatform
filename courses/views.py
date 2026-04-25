from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import LessonForm, StudyGroupForm, VideoLessonForm
from .mixins import AdminOrTeacherMixin, GroupTeacherMixin, LessonOwnerMixin
from .models import Lesson, StudyGroup, VideoLesson


class GroupListView(LoginRequiredMixin, ListView):
    model = StudyGroup
    template_name = "courses/group_list.html"
    context_object_name = "groups"

    def get_queryset(self):
        user = self.request.user
        if user.role == "admin":
            return StudyGroup.objects.all()
        if user.role == "teacher":
            return StudyGroup.objects.filter(teachers=user)
        if user.role == "student":
            return StudyGroup.objects.filter(students=user)
        return StudyGroup.objects.none()


class GroupDetailView(LoginRequiredMixin, DetailView):
    model = StudyGroup
    template_name = "courses/group_detail.html"
    context_object_name = "group"

    def get_queryset(self):
        user = self.request.user
        if user.role == "admin":
            return StudyGroup.objects.all()
        if user.role == "teacher":
            return StudyGroup.objects.filter(teachers=user)
        if user.role == "student":
            return StudyGroup.objects.filter(students=user)
        return StudyGroup.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        content_type = self.request.GET.get("content_type", "lessons")
        if content_type not in {"lessons", "video_lessons"}:
            content_type = "lessons"

        search_query = self.request.GET.get("q", "").strip()

        lessons = self.object.lessons.all()
        if search_query:
            lessons = lessons.filter(
                Q(subject__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(homework__icontains=search_query)
            )

        video_lessons = self.object.video_lessons.all()
        if search_query:
            video_lessons = video_lessons.filter(
                Q(title__icontains=search_query) | Q(description__icontains=search_query)
            )

        context["content_type"] = content_type
        context["search_query"] = search_query
        context["lessons"] = lessons
        context["video_lessons"] = video_lessons
        context["lessons_count"] = self.object.lessons.count()
        context["video_lessons_count"] = self.object.video_lessons.count()
        return context


class GroupCreateView(AdminOrTeacherMixin, CreateView):
    model = StudyGroup
    form_class = StudyGroupForm
    template_name = "courses/group_form.html"
    success_url = reverse_lazy("courses:group_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        # Преподаватель, создавший группу, автоматически добавляется в неё
        if self.request.user.role == "teacher":
            self.object.teachers.add(self.request.user)
        return response


class LessonCreateView(GroupTeacherMixin, CreateView):
    model = Lesson
    form_class = LessonForm
    template_name = "courses/lesson_form.html"

    def get_success_url(self):
        return reverse("courses:group_detail", kwargs={"pk": self.kwargs["pk"]})

    def form_valid(self, form):
        form.instance.group = self.get_group()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["group"] = self.get_group()
        return context


class LessonUpdateView(LessonOwnerMixin, UpdateView):
    model = Lesson
    form_class = LessonForm
    template_name = "courses/lesson_form.html"

    def get_success_url(self):
        return reverse("courses:group_detail", kwargs={"pk": self.get_lesson().group.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["group"] = self.get_lesson().group
        context["editing"] = True
        return context


class LessonDeleteView(LessonOwnerMixin, DeleteView):
    model = Lesson
    template_name = "courses/lesson_confirm_delete.html"

    def get_success_url(self):
        return reverse("courses:group_detail", kwargs={"pk": self.get_lesson().group.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["group"] = self.get_lesson().group
        return context


class VideoLessonCreateView(AdminOrTeacherMixin, CreateView):
    model = VideoLesson
    form_class = VideoLessonForm
    template_name = "courses/video_lesson_form.html"
    success_url = reverse_lazy("courses:group_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        return super().form_valid(form)
