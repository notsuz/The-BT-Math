from rest_framework import serializers

from apps.catalog.api.serializers import CourseListSerializer
from apps.catalog.models import Course

from ..models import Order


class OrderSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        source="course", queryset=Course.objects.filter(is_published=True), write_only=True
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "course",
            "course_id",
            "transaction_uuid",
            "amount",
            "gateway",
            "gateway_reference",
            "status",
            "created_at",
        ]
        read_only_fields = ["transaction_uuid", "amount", "gateway_reference", "status", "created_at"]

    def create(self, validated_data):
        course = validated_data["course"]
        validated_data["amount"] = course.price
        validated_data["student"] = self.context["request"].user
        return super().create(validated_data)
