from rest_framework.routers import DefaultRouter

from .views import OrderViewSet

app_name = "orders_api"

router = DefaultRouter()
router.register("orders", OrderViewSet, basename="order")

urlpatterns = router.urls
