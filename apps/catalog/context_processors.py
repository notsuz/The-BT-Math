from django.core.cache import cache

from .models import Category


def navigation(request):
    """Expose the category/program tree to every template for the main nav."""
    nav_categories = cache.get("nav_categories")
    if nav_categories is None:
        nav_categories = list(
            Category.objects.prefetch_related("programs").all()
        )
        cache.set("nav_categories", nav_categories, 300)
    return {"nav_categories": nav_categories}
