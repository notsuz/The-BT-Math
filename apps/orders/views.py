from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import DetailView, ListView, TemplateView

from apps.catalog.models import Course

from .models import Order


class CheckoutView(LoginRequiredMixin, DetailView):
    model = Course
    pk_url_kwarg = "pk"
    template_name = "orders/checkout.html"
    context_object_name = "course"

    def get_queryset(self):
        return Course.objects.filter(is_published=True)

    def get(self, request, *args, **kwargs):
        course = self.get_object()
        if course.user_has_access(request.user):
            return redirect(course.get_absolute_url())
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        course = self.get_object()
        if course.user_has_access(request.user):
            return redirect(course.get_absolute_url())

        gateway = request.POST.get("gateway")
        if gateway not in Order.Gateway.values:
            return render(
                self.request,
                self.template_name,
                {"course": course, "error": "Please select a valid payment method."},
            )

        order = Order.objects.create(
            student=request.user,
            course=course,
            amount=course.price,
            gateway=gateway,
        )
        return redirect(reverse("payments:initiate", args=[order.transaction_uuid]))


class MyCoursesView(LoginRequiredMixin, ListView):
    template_name = "orders/my_courses.html"
    context_object_name = "courses"

    def get_queryset(self):
        return Course.objects.filter(
            orders__student=self.request.user, orders__status=Order.Status.SUCCESS
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recent_orders"] = Order.objects.filter(student=self.request.user)[:10]
        return context


class PaymentSuccessView(LoginRequiredMixin, TemplateView):
    template_name = "orders/payment_success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = get_object_or_404(
            Order, transaction_uuid=self.request.GET.get("order"), student=self.request.user
        )
        context["order"] = order
        return context


class PaymentFailureView(LoginRequiredMixin, TemplateView):
    template_name = "orders/payment_failure.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = Order.objects.filter(
            transaction_uuid=self.request.GET.get("order"), student=self.request.user
        ).first()
        context["order"] = order
        return context
