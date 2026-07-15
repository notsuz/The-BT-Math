from django.urls import path

from .views import (
    CategoryDetailView,
    CourseDetailView,
    CourseSearchView,
    ProgramDetailView,
    ProtectedContentView,
)

app_name = "catalog"

urlpatterns = [
    path("search/", CourseSearchView.as_view(), name="course_search"),
    path("content/<int:pk>/download/", ProtectedContentView.as_view(), name="content_download"),
    path("<slug:category_slug>/", CategoryDetailView.as_view(), name="category_detail"),
    path(
        "<slug:category_slug>/<slug:program_slug>/",
        ProgramDetailView.as_view(),
        name="program_detail",
    ),
    path(
        "<slug:category_slug>/<slug:program_slug>/<slug:course_slug>/",
        CourseDetailView.as_view(),
        name="course_detail",
    ),
]
