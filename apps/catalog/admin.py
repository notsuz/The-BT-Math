from django.contrib import admin

from .models import Category, Chapter, ContentItem, Course, Program


class ProgramInline(admin.TabularInline):
    model = Program
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "order"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProgramInline]


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "order"]
    list_filter = ["category"]
    prepopulated_fields = {"slug": ("name",)}


class ContentItemInline(admin.TabularInline):
    model = ContentItem
    extra = 1


class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 1
    show_change_link = True


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["title", "program", "price", "is_published", "created_at"]
    list_filter = ["program__category", "program", "is_published"]
    search_fields = ["title", "description"]
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ChapterInline]


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ["title", "course", "order", "is_free"]
    list_filter = ["course__program__category", "is_free"]
    inlines = [ContentItemInline]


@admin.register(ContentItem)
class ContentItemAdmin(admin.ModelAdmin):
    list_display = ["title", "chapter", "content_type", "is_free"]
    list_filter = ["content_type", "is_free"]
