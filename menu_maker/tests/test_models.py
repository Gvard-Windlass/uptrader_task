from django.test import TestCase
from menu_maker.models import MenuItem


class TestMenuItemModel(TestCase):
    def test_create_menu_item(self):
        menu_item = MenuItem.objects.create(name="test item", lft=1, rgt=2)
        self.assertIsInstance(menu_item, MenuItem)
