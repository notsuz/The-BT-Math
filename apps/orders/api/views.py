from rest_framework import mixins, permissions, viewsets

from ..models import Order
from .serializers import OrderSerializer


class OrderViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """Students can list/retrieve their own orders and create a new (pending)
    one. Status transitions happen server-side via the payments app only."""

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(student=self.request.user).select_related("course")
