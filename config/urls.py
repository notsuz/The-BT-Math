from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

admin.site.site_header = f"{settings.SITE_NAME} Administration"
admin.site.site_title = f"{settings.SITE_NAME} Admin"
admin.site.index_title = "Dashboard"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.pages.urls")),
    path("accounts/", include("apps.users.urls")),
    path("orders/", include("apps.orders.urls")),
    path("payments/", include("apps.payments.urls")),
    path("courses/", include("apps.catalog.urls")),
    # API
    path("api/v1/", include("apps.users.api.urls")),
    path("api/v1/", include("apps.catalog.api.urls")),
    path("api/v1/", include("apps.orders.api.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)