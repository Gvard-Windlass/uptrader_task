from typing import Any
from django.core.management.base import BaseCommand
from menu_maker.models import MenuItem

menu_data = [
    ["Clothing", 1, 22],
    ["Men's", 2, 9, 1],
    ["Women's", 10, 21, 1],
    ["Suits", 3, 8, 2],
    ["Slacks", 4, 5, 4],
    ["Jackets", 6, 7, 4],
    ["Dresses", 11, 16, 3],
    ["Skirts", 17, 18, 3],
    ["Blouses", 19, 20, 3],
    ["Evening Gowns", 12, 13, 7],
    ["Sun Dresses", 14, 15, 7],
    ["Electronics", 23, 42],
    ["Home", 24, 29, 12],
    ["Computers", 30, 35, 12],
    ["Portable", 36, 41, 12],
    ["Freezers", 25, 26, 13],
    ["Microwaves", 27, 28, 13],
    ["PC", 31, 32, 14],
    ["Laptops", 33, 34, 14],
    ["Smartphones", 37, 38, 15],
    ["Smartwatches", 39, 40, 15],
]


class Command(BaseCommand):
    help = "Load sample menu tree"

    def handle(self, *args: Any, **options: Any) -> None:
        for item in menu_data:
            if len(item) > 3:
                parent = MenuItem.objects.get(id=item[3])
            else:
                parent = None

            item, created = MenuItem.objects.get_or_create(
                name=item[0],
                defaults={"lft": item[1], "rgt": item[2], "parent": parent},
            )

            if created:
                print(f"Created menu item for {item.name}")
