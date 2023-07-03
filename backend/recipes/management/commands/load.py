import json

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Загрузка данных'

    def handle(self, *args, **kwargs):
        data_path = settings.BASE_DIR
        with open(
            f'{data_path}/data/ingredients.json',
            'r',
            encoding='utf-8'
        ) as file:
            reader = json.load(file)
            Ingredient.objects.bulk_create(
                Ingredient(**data) for data in reader)
        data = [
            {'name': 'Завтрак', 'color': '#E26C2D', 'slug': 'breakfast'},
            {'name': 'Обед', 'color': '#49B64E', 'slug': 'dinner'},
            {'name': 'Ужин', 'color': '#8775D2', 'slug': 'supper'}]
        Tag.objects.bulk_create(Tag(**tag) for tag in data)
        self.stdout.write(self.style.SUCCESS('Данные загружены!'))
