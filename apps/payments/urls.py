from django.urls import path

from .views import EsewaCallbackView, InitiatePaymentView, KhaltiCallbackView

app_name = "payments"

urlpatterns = [
    path("initiate/<uuid:transaction_uuid>/", InitiatePaymentView.as_view(), name="initiate"),
    path("esewa/callback/", EsewaCallbackView.as_view(), name="esewa_callback"),
    path("khalti/callback/", KhaltiCallbackView.as_view(), name="khalti_callback"),
]
