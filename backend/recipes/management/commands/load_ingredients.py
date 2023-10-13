import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Load data ingredients'

    def handle(self, *args, **options):
        with open('data/ingredients.csv', encoding='utf8') as file:
            reader = csv.reader(file)
            for name, measurement_unit in reader:
                ingredient, created = Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit
                )
        print('OK')
