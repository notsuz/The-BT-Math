from django.db.models import Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView

from .models import Category, Chapter, ContentItem, Course, Program


class CategoryDetailView(DetailView):
    model = Category
    slug_url_kwarg = "category_slug"
    template_name = "catalog/category_detail.html"
    context_object_name = "category"

    def get_queryset(self):
        return Category.objects.prefetch_related("programs")


class ProgramDetailView(DetailView):
    model = Program
    slug_url_kwarg = "program_slug"
    template_name = "catalog/program_detail.html"
    context_object_name = "program"

    def get_queryset(self):
        return Program.objects.filter(category__slug=self.kwargs["category_slug"]).select_related(
            "category"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["courses"] = self.object.courses.filter(is_published=True)
        return context


class CourseDetailView(DetailView):
    model = Course
    slug_url_kwarg = "course_slug"
    template_name = "catalog/course_detail.html"
    context_object_name = "course"

    def get_queryset(self):
        return Course.objects.filter(
            program__slug=self.kwargs["program_slug"],
            program__category__slug=self.kwargs["category_slug"],
            is_published=True,
        ).select_related("program", "program__category")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        context["chapters"] = course.chapters.prefetch_related("content_items")
        context["has_access"] = course.user_has_access(self.request.user)
        return context


class CourseSearchView(ListView):
    """Lets a student search for a subject's notes, e.g. a BCA student typing
    'Digital Logic' to jump straight to that subject's chapter/notes page."""

    model = Course
    template_name = "catalog/search_results.html"
    context_object_name = "courses"
    paginate_by = 12

    def get_queryset(self):
        self.query = self.request.GET.get("q", "").strip()
        self.program_id = self.request.GET.get("program", "").strip()
        qs = Course.objects.filter(is_published=True).select_related(
            "program", "program__category"
        )
        if self.query:
            qs = qs.filter(
                Q(title__icontains=self.query)
                | Q(description__icontains=self.query)
                | Q(program__name__icontains=self.query)
            )
        if self.program_id.isdigit():
            qs = qs.filter(program_id=self.program_id)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.query
        context["selected_program_id"] = self.program_id
        context["programs"] = Program.objects.select_related("category")
        return context


class ProtectedContentView(DetailView):
    """Streams a ContentItem's file only if it's free or the user purchased
    the parent course. This is the *only* code path that ever reads from
    PRIVATE_MEDIA_ROOT - there is no public URL to the file itself."""

    model = ContentItem
    pk_url_kwarg = "pk"

    def get(self, request, *args, **kwargs):
        item = get_object_or_404(
            ContentItem.objects.select_related("chapter__course"), pk=kwargs["pk"]
        )
        course = item.chapter.course
        if not (item.is_free or item.chapter.is_free or course.user_has_access(request.user)):
            raise Http404("Content not available.")
        if not item.file:
            raise Http404("No file attached to this content item.")
        return FileResponse(item.file.open("rb"), as_attachment=False, filename=item.file.name.split("/")[-1])
