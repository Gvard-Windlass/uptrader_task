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
        items_by_id = MenuItem.objects.get_tree(7)
        items_by_name = MenuItem.objects.get_tree("Dresses")
        self.assertEqual(len(items_by_id), 3)
        self.assertEqual(len(items_by_name), 3)
        self.assertRaises(TypeError, MenuItem.objects.get_tree, [])

    def test_get_position(self):
        root = MenuItem.objects.get(name="Clothing")
        node1 = MenuItem.objects.get(name="Dresses")
        node2 = MenuItem.objects.get(name="Blouses")
        self.assertEqual(root.get_position(), None)
        self.assertEqual(node1.get_position(), (1, 3))
        self.assertEqual(node2.get_position(), (3, 3))
