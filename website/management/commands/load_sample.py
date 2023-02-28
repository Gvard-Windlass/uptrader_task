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
