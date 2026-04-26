from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.db.models import Count, DecimalField, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import redirect
from django.utils.dateparse import parse_date
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView, View

from .forms import LessonForm, StudyGroupForm, VideoLessonForm
from .mixins import AdminOnlyMixin, AdminOrTeacherMixin, GroupTeacherMixin, LessonOwnerMixin
from .models import Lesson, LessonAttachment, StudyGroup, VideoLesson


class GroupListView(LoginRequiredMixin, ListView):
    model = StudyGroup
    template_name = "courses/group_list.html"
    context_object_name = "groups"
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        base = StudyGroup.objects.prefetch_related("students")
        if user.role == "admin":
            queryset = base
        elif user.role == "teacher":
            queryset = base.filter(teachers=user)
        elif user.role == "student":
            queryset = base.filter(students=user)
        else:
            queryset = StudyGroup.objects.none()

        search_query = self.request.GET.get("q", "").strip()
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "").strip()
        return context


class GroupDetailView(LoginRequiredMixin, DetailView):
    model = StudyGroup
    template_name = "courses/group_detail.html"
    context_object_name = "group"

    def get_queryset(self):
        user = self.request.user
        base = StudyGroup.objects.prefetch_related(
            "students",
            "teachers",
            "lessons",
            "lessons__attachments",
            "video_lessons",
        )
        if user.role == "admin":
            return base
        if user.role == "teacher":
            return base.filter(teachers=user)
        if user.role == "student":
            return base.filter(students=user)
        return StudyGroup.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        content_type = self.request.GET.get("content_type", "lessons")
        if content_type not in {"lessons", "video_lessons"}:
            content_type = "lessons"

        search_query = self.request.GET.get("q", "").strip()
        status_filter = self.request.GET.get("status", "").strip()

        lessons = self.object.lessons.all()
        if status_filter in Lesson.Status.values:
            lessons = lessons.filter(status=status_filter)
        if search_query:
            matched_subject_codes = [
                code
                for code, label in Lesson.Subject.choices
                if search_query.casefold() in code.casefold()
                or search_query.casefold() in label.casefold()
            ]
            lessons = lessons.filter(
                Q(subject__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(homework__icontains=search_query)
                | Q(subject__in=matched_subject_codes)
            )

        video_lessons = self.object.video_lessons.all()
        if search_query:
            video_lessons = video_lessons.filter(
                Q(title__icontains=search_query)
                | Q(description__icontains=search_query)
            )

        context["content_type"] = content_type
        context["search_query"] = search_query
        context["status_filter"] = status_filter
        context["status_options"] = Lesson.Status.choices
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
        response = super().form_valid(form)
        self._save_attachments(self.object)
        return response

    def _save_attachments(self, lesson):
        for attachment in self.request.FILES.getlist("attachments"):
            LessonAttachment.objects.create(lesson=lesson, file=attachment)

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
        context["existing_attachments"] = self.get_lesson().attachments.all()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        delete_ids = self.request.POST.getlist("delete_attachments")
        if delete_ids:
            self.object.attachments.filter(id__in=delete_ids).delete()
        for attachment in self.request.FILES.getlist("attachments"):
            LessonAttachment.objects.create(lesson=self.object, file=attachment)
        return response


class LessonDeleteView(LessonOwnerMixin, DeleteView):
    model = Lesson
    template_name = "courses/lesson_confirm_delete.html"

    def get_success_url(self):
        return reverse("courses:group_detail", kwargs={"pk": self.get_lesson().group.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["group"] = self.get_lesson().group
        return context


class LessonDuplicateView(LessonOwnerMixin, View):
    def post(self, request, *args, **kwargs):
        source_lesson = self.get_lesson()
        Lesson.objects.create(
            group=source_lesson.group,
            subject=source_lesson.subject,
            status=Lesson.Status.DRAFT,
            duration_minutes=source_lesson.duration_minutes,
            cost=source_lesson.cost,
            description=source_lesson.description,
            homework=source_lesson.homework,
        )
        return redirect("courses:group_detail", pk=source_lesson.group.pk)


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


class AdminStatisticsView(AdminOnlyMixin, TemplateView):
    template_name = "courses/admin_statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_model = get_user_model()
        teachers = user_model.objects.filter(role=user_model.Role.TEACHER).order_by(
            "last_name",
            "first_name",
            "username",
        )

        selected_teacher = self.request.GET.get("teacher", "").strip()
        start_date_raw = self.request.GET.get("start_date", "").strip()
        end_date_raw = self.request.GET.get("end_date", "").strip()

        start_date = parse_date(start_date_raw) if start_date_raw else None
        end_date = parse_date(end_date_raw) if end_date_raw else None
        date_error = bool((start_date_raw and start_date is None) or (end_date_raw and end_date is None))

        lessons = Lesson.objects.all()
        lesson_filter = Q()
        if start_date:
            lessons = lessons.filter(created_at__date__gte=start_date)
            lesson_filter &= Q(taught_groups__lessons__created_at__date__gte=start_date)
        if end_date:
            lessons = lessons.filter(created_at__date__lte=end_date)
            lesson_filter &= Q(taught_groups__lessons__created_at__date__lte=end_date)
        if selected_teacher:
            lessons = lessons.filter(group__teachers__id=selected_teacher)

        money_field = DecimalField(max_digits=10, decimal_places=2)
        teacher_stats = teachers.annotate(
            lessons_count=Count("taught_groups__lessons", filter=lesson_filter, distinct=True),
            total_duration=Coalesce(
                Sum("taught_groups__lessons__duration_minutes", filter=lesson_filter),
                Value(0),
            ),
            total_cost=Coalesce(
                Sum("taught_groups__lessons__cost", filter=lesson_filter, output_field=money_field),
                Value(0),
                output_field=money_field,
            ),
        )

        if selected_teacher:
            teacher_stats = teacher_stats.filter(id=selected_teacher)

        overall = lessons.aggregate(
            lessons_count=Count("id"),
            total_duration=Coalesce(Sum("duration_minutes"), Value(0)),
            total_cost=Coalesce(
                Sum("cost", output_field=money_field),
                Value(0),
                output_field=money_field,
            ),
        )

        context.update({
            "teachers": teachers,
            "teacher_stats": teacher_stats,
            "selected_teacher": selected_teacher,
            "start_date": start_date_raw,
            "end_date": end_date_raw,
            "date_error": date_error,
            "overall": overall,
        })
        return context
