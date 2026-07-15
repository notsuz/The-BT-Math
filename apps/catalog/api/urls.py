from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, CourseViewSet, ProgramViewSet

app_name = "catalog_api"

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("programs", ProgramViewSet, basename="program")
router.register("courses", CourseViewSet, basename="course")

urlpatterns = router.urls
