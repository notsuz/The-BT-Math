from django.urls import path

from .views import CheckoutView, MyCoursesView, PaymentFailureView, PaymentSuccessView

app_name = "orders"

urlpatterns = [
    path("my-courses/", MyCoursesView.as_view(), name="my_courses"),
    path("checkout/<int:pk>/", CheckoutView.as_view(), name="checkout"),
    path("payment/success/", PaymentSuccessView.as_view(), name="payment_success"),
    path("payment/failure/", PaymentFailureView.as_view(), name="payment_failure"),
]
