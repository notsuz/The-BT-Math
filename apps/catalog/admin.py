from django import forms
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
    search_fields = ["name", "category__name"]
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
    list_select_related = ["program", "program__category"]
    search_fields = ["title", "description", "program__name", "program__category__name"]
    autocomplete_fields = ["program"]
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ChapterInline]


class CascadingSelect(forms.Select):
    """Tags each <option> with data-{filter_attr}=<parent id> so admin JS can
    filter this dropdown down to whichever value was picked in the field
    above it (see admin-chapter-cascade.js)."""

    def __init__(self, *args, filter_attr, value_map=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.filter_attr = filter_attr
        self.value_map = value_map or {}

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        key = getattr(value, "value", value)
        parent_id = self.value_map.get(key)
        if parent_id is not None:
            option["attrs"][f"data-{self.filter_attr}"] = parent_id
        return option


class ChapterAdminForm(forms.ModelForm):
    # `category` and `program` are not model fields - they only exist so the
    # admin can narrow Category -> Program -> Course step by step instead of
    # picking a course out of every course in every program at once.
    category = forms.ModelChoiceField(
        queryset=Category.objects.order_by("order", "name"),
        required=False,
        label="Category",
        help_text="Pick a category to filter the Program list below.",
    )
    program = forms.ModelChoiceField(
        queryset=Program.objects.select_related("category").order_by(
            "category__order", "category__name", "order", "name"
        ),
        required=False,
        label="Program",
        help_text="Pick a program to filter the Course list below.",
    )

    class Meta:
        model = Chapter
        fields = ["category", "program", "course", "title", "order", "is_free"]

    class Media:
        js = ["js/admin-chapter-cascade.js"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        programs = Program.objects.select_related("category").order_by(
            "category__order", "category__name", "order", "name"
        )
        self.fields["program"].widget = CascadingSelect(
            filter_attr="category", value_map={p.pk: p.category_id for p in programs}
        )
        self.fields["program"].queryset = programs

        courses = Course.objects.select_related("program", "program__category").order_by(
            "program__category__order",
            "program__category__name",
            "program__order",
            "program__name",
            "title",
        )
        self.fields["course"].widget = CascadingSelect(
            filter_attr="program", value_map={c.pk: c.program_id for c in courses}
        )
        self.fields["course"].queryset = courses

        if self.instance.pk and self.instance.course_id:
            self.fields["program"].initial = self.instance.course.program_id
            self.fields["category"].initial = self.instance.course.program.category_id

        # Explicit order: category -> program -> course -> the rest.
        self.fields = {
            name: self.fields[name]
            for name in ["category", "program", "course", "title", "order", "is_free"]
        }


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    form = ChapterAdminForm
    list_display = ["title", "course", "order", "is_free"]
    list_filter = ["course__program__category", "course__program", "course", "is_free"]
    list_select_related = ["course", "course__program", "course__program__category"]
    search_fields = ["title", "course__title", "course__program__name"]
    inlines = [ContentItemInline]

    class Media:
        js = ["js/admin-chapterlist-cascade.js"]

    def changelist_view(self, request, extra_context=None):
        # Fed to admin-chapterlist-cascade.js so the category/program/course
        # filter dropdowns in the changelist toolbar can narrow each other
        # down, same cascade idea as the add-form (see ChapterAdminForm).
        category_to_programs = {}
        for program in Program.objects.order_by("category__order", "category__name", "order", "name"):
            category_to_programs.setdefault(str(program.category_id), []).append(program.pk)

        program_to_courses = {}
        for course in Course.objects.order_by("program__category__order", "program__order", "title"):
            program_to_courses.setdefault(str(course.program_id), []).append(course.pk)

        extra_context = extra_context or {}
        extra_context["category_to_programs"] = category_to_programs
        extra_context["program_to_courses"] = program_to_courses
        return super().changelist_view(request, extra_context=extra_context)

    def render_change_form(self, request, context, add=False, change=False, form_url="", obj=None):
        # Fed to admin-chapter-cascade.js as a course_id -> [chapters] map so
        # it can show "chapters already in this course" next to the picker,
        # without a separate AJAX round trip for a dataset this small.
        chapters_by_course = {}
        for chapter in Chapter.objects.select_related("course").order_by("course_id", "order", "id"):
            chapters_by_course.setdefault(chapter.course_id, []).append(
                {"title": chapter.title, "order": chapter.order, "is_free": chapter.is_free}
            )
        context["chapters_by_course"] = chapters_by_course
        return super().render_change_form(request, context, add, change, form_url, obj)


@admin.register(ContentItem)
class ContentItemAdmin(admin.ModelAdmin):
    list_display = ["title", "chapter", "content_type", "is_free"]
    list_filter = ["content_type", "is_free"]
    search_fields = ["title", "chapter__title", "chapter__course__title"]
    autocomplete_fields = ["chapter"]
