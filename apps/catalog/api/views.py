from rest_framework import permissions, viewsets

from ..models import Category, Course, Program
from .serializers import (
    CategorySerializer,
    CourseDetailSerializer,
    CourseListSerializer,
    ProgramSerializer,
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.prefetch_related("programs").all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"


class ProgramViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Program.objects.select_related("category").all()
    serializer_class = ProgramSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        qs = super().get_queryset()
        category_slug = self.request.query_params.get("category")
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        return qs


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.filter(is_published=True).select_related("program", "program__category")
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CourseDetailSerializer
        return CourseListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        program_slug = self.request.query_params.get("program")
        if program_slug:
            qs = qs.filter(program__slug=program_slug)
        return qs
