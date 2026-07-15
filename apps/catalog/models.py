from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from .storage import PrivateMediaStorage


class Category(models.Model):
    """Top-level nav section: +2, IOE, Bachelors, Masters."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:category_detail", args=[self.slug])


class Program(models.Model):
    """A program under a category: Grade 11, BCA, MBA, IOE, etc."""

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="programs")
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        unique_together = ["category", "slug"]

    def __str__(self):
        return f"{self.category.name} / {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:program_detail", args=[self.category.slug, self.slug])


class Course(models.Model):
    """A purchasable course, e.g. 'Physics - Grade XII', belonging to a program."""

    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="courses")
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, blank=True)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to="course_thumbnails/", blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]
        unique_together = ["program", "slug"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            "catalog:course_detail",
            args=[self.program.category.slug, self.program.slug, self.slug],
        )

    def is_free(self):
        return self.price == 0

    def user_has_access(self, user):
        if self.is_free():
            return True
        if not user or not user.is_authenticated:
            return False
        return self.orders.filter(student=user, status="success").exists()


class Chapter(models.Model):
    """An ordered chapter within a course."""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="chapters")
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    is_free = models.BooleanField(
        default=False, help_text="If set, this chapter's content is viewable without purchase."
    )

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class ContentItem(models.Model):
    """A single piece of content (PDF, past question, tutorial, past trick) in a chapter."""

    class ContentType(models.TextChoices):
        PDF_NOTES = "pdf_notes", "PDF Notes"
        PAST_QUESTION = "past_question", "Past Question"
        TUTORIAL = "tutorial", "Tutorial (Video)"
        PAST_TRICK = "past_trick", "Past Trick"

    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name="content_items")
    content_type = models.CharField(max_length=20, choices=ContentType.choices)
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    is_free = models.BooleanField(
        default=False, help_text="If set, viewable/downloadable without purchase."
    )
    # Locked files are written to PRIVATE_MEDIA_ROOT (see settings) and are
    # only ever streamed through catalog.views.ProtectedContentView, so there
    # is no public URL for paid content.
    file = models.FileField(
        upload_to="content/%Y/%m/", storage=PrivateMediaStorage(), blank=True, null=True
    )
    video_url = models.URLField(blank=True, help_text="Used for Tutorial content type.")

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.chapter} - {self.title}"
