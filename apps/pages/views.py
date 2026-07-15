from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from apps.catalog.models import Category, Course


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.prefetch_related("programs")
        context["featured_courses"] = Course.objects.filter(is_published=True).select_related(
            "program", "program__category"
        )[:8]
        return context


class AboutView(TemplateView):
    template_name = "pages/about.html"


class TermsView(TemplateView):
    template_name = "pages/terms.html"


class PrivacyView(TemplateView):
    template_name = "pages/privacy.html"


class ContactView(TemplateView):
    template_name = "pages/contact.html"

    def post(self, request, *args, **kwargs):
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()

        if name and email and message:
            send_mail(
                subject=f"[Contact] Message from {name}",
                message=f"From: {name} <{email}>\n\n{message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )
            messages.success(request, "Thanks for reaching out! We'll get back to you soon.")
        else:
            messages.error(request, "Please fill in all fields.")
        return redirect(reverse_lazy("pages:contact"))
