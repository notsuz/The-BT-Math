from rest_framework import serializers

from ..models import Category, Chapter, ContentItem, Course, Program


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "order"]


class ProgramSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Program
        fields = ["id", "category", "name", "slug", "description", "order"]


class CourseListSerializer(serializers.ModelSerializer):
    program = ProgramSerializer(read_only=True)

    class Meta:
        model = Course
        fields = ["id", "program", "title", "slug", "thumbnail", "price", "is_published"]


class ContentItemSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = ContentItem
        fields = [
            "id",
            "content_type",
            "title",
            "order",
            "is_free",
            "video_url",
            "download_url",
        ]

    def get_download_url(self, obj) -> str | None:
        if not obj.file:
            return None
        request = self.context.get("request")
        path = f"/courses/content/{obj.id}/download/"
        return request.build_absolute_uri(path) if request else path


class ChapterSerializer(serializers.ModelSerializer):
    content_items = ContentItemSerializer(many=True, read_only=True)

    class Meta:
        model = Chapter
        fields = ["id", "title", "order", "is_free", "content_items"]


class CourseDetailSerializer(serializers.ModelSerializer):
    program = ProgramSerializer(read_only=True)
    chapters = ChapterSerializer(many=True, read_only=True)
    has_access = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id",
            "program",
            "title",
            "slug",
            "description",
            "thumbnail",
            "price",
            "is_published",
            "chapters",
            "has_access",
        ]

    def get_has_access(self, obj) -> bool:
        request = self.context.get("request")
        user = getattr(request, "user", None)
        return obj.user_has_access(user)
