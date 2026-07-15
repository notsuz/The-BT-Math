from django.core.management.base import BaseCommand
from django.db import transaction

from apps.catalog.models import Category, Chapter, ContentItem, Course, Program

DEMO_TREE = {
    "+2": ["Grade 11", "Grade 12"],
    "IOE": ["Past Questions", "Past Tricks"],
    "Bachelors": ["BBA", "BSC", "BIT", "BCA", "BE", "BSC.CSIT"],
    "Masters": ["MBS", "MBA", "MSC"],
}

# slugify("+2") collapses to just "2", which makes for a confusing URL -
# give it an explicit, readable slug instead.
CATEGORY_SLUG_OVERRIDES = {
    "+2": "plus-two",
}


class Command(BaseCommand):
    help = "Seed the catalog with the navigation tree from the requirements doc, plus one demo course."

    @transaction.atomic
    def handle(self, *args, **options):
        for order, (category_name, program_names) in enumerate(DEMO_TREE.items()):
            defaults = {"order": order}
            if category_name in CATEGORY_SLUG_OVERRIDES:
                defaults["slug"] = CATEGORY_SLUG_OVERRIDES[category_name]
            category, _ = Category.objects.get_or_create(name=category_name, defaults=defaults)
            for p_order, program_name in enumerate(program_names):
                Program.objects.get_or_create(
                    category=category, name=program_name, defaults={"order": p_order}
                )

        bca = Program.objects.get(category__name="Bachelors", name="BCA")
        course, _ = Course.objects.get_or_create(
            program=bca,
            title="Programming in C - BCA First Semester",
            defaults={
                "description": "Chapter-wise notes, past questions and tutorials for C programming.",
                "price": 499,
            },
        )
        ch1, _ = Chapter.objects.get_or_create(
            course=course, title="Introduction to C", defaults={"order": 1, "is_free": True}
        )
        ch2, _ = Chapter.objects.get_or_create(
            course=course, title="Loops and Control Structures", defaults={"order": 2, "is_free": False}
        )
        ContentItem.objects.get_or_create(
            chapter=ch1,
            title="Intro Tutorial",
            defaults={
                "content_type": ContentItem.ContentType.TUTORIAL,
                "order": 1,
                "is_free": True,
                "video_url": "https://www.youtube.com/watch?v=KJgsSFOSQv0",
            },
        )
        ContentItem.objects.get_or_create(
            chapter=ch2,
            title="Chapter 2 Notes (PDF)",
            defaults={"content_type": ContentItem.ContentType.PDF_NOTES, "order": 1, "is_free": False},
        )

        self.stdout.write(self.style.SUCCESS("Demo catalog data seeded."))
