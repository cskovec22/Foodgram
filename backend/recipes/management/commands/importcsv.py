import csv

from django.core.management.base import BaseCommand

from foodgram_backend.settings import CSV_FILES_DIR
from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    """Импорт ингредиентов и тегов в базу данных."""

    help = "Импортирует данные из csv в базу данных"

    def handle(self, *args, **options):
        self.import_ingredients()
        self.import_tags()

    def import_ingredients(self):
        """Импорт ингредиентов в базу данных."""
        with open(
            f'{CSV_FILES_DIR}/ingredients.csv', newline="", encoding="utf-8"
        ) as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for row in reader:
                Ingredient.objects.create(name=row[0], measurement_unit=row[1])
            self.stdout.write(self.style.SUCCESS("Ингредиенты загружены."))

    def import_tags(self):
        """Импорт тегов в базу данных."""
        with open(
            f'{CSV_FILES_DIR}/tags.csv', newline="", encoding="utf-8"
        ) as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for row in reader:
                Tag.objects.create(name=row[0], color=row[1], slug=row[2])
            self.stdout.write(self.style.SUCCESS("Теги загружены."))
