from django.test import TestCase
from menu_maker.models import MenuItem


class TestMenuItemModel(TestCase):
    fixtures = ["menu_maker.json"]

    def test_create_menu_item(self):
        menu_item = MenuItem.objects.create(name="test item", lft=1, rgt=2)
        self.assertIsInstance(menu_item, MenuItem)

    def test_get_menu_items(self):
        items = MenuItem.objects.all()
        self.assertEqual(len(items), 11)

    def test_get_descendants(self):
        items = MenuItem.objects.get_descendants(3)
        self.assertEqual(len(items), 5)
        items = MenuItem.objects.get_descendants(3, direct_only=True)
        self.assertEqual(len(items), 3)

    def test_get_tree(self):
        items = MenuItem.objects.get_tree_by_id(7)
        self.assertEqual(len(items), 3)
