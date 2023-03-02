from django.test import TestCase
from menu_maker.models import MenuItem


class TestMenuItemModelWithFixtures(TestCase):
    fixtures = ["menu_maker.json"]

    def _get_tree_values(self):
        return MenuItem.objects.order_by("id").values_list("name", "lft", "rgt")

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

    def test_create_new_root(self):
        new_root = MenuItem(name="new root", lft=0, rgt=0)
        new_root.save()

        actual_values = self._get_tree_values()
        expected_values = [
            ("Clothing", 1, 22),
            ("Men's", 2, 9),
            ("Women's", 10, 21),
            ("Suits", 3, 8),
            ("Slacks", 4, 5),
            ("Jackets", 6, 7),
            ("Dresses", 11, 16),
            ("Skirts", 17, 18),
            ("Blouses", 19, 20),
            ("Evening Gowns", 12, 13),
            ("Sun Dresses", 14, 15),
            ("new root", 23, 24),
        ]

        self.assertCountEqual(actual_values, expected_values)

    def test_add_child_item_default(self):
        parent_node = MenuItem.objects.get(name="Women's")
        new_node = MenuItem(name="new item", lft=0, rgt=0, parent=parent_node)

        new_node.save()

        actual_values = self._get_tree_values()
        expected_values = [
            ("Clothing", 1, 24),
            ("Men's", 2, 9),
            ("Women's", 10, 23),
            ("Suits", 3, 8),
            ("Slacks", 4, 5),
            ("Jackets", 6, 7),
            ("Dresses", 11, 16),
            ("Skirts", 17, 18),
            ("Blouses", 19, 20),
            ("Evening Gowns", 12, 13),
            ("Sun Dresses", 14, 15),
            ("new item", 21, 22),
        ]

        self.assertCountEqual(actual_values, expected_values)
        self.assertEqual(new_node.get_position(), (4, 4))

    def test_add_child_item_positioned(self):
        parent_node = MenuItem.objects.get(name="Women's")
        new_node = MenuItem(name="new item", lft=0, rgt=0, parent=parent_node)
        new_node.set_new_position(2)

        new_node.save()

        actual_values = self._get_tree_values()
        expected_values = [
            ("Clothing", 1, 24),
            ("Men's", 2, 9),
            ("Women's", 10, 23),
            ("Suits", 3, 8),
            ("Slacks", 4, 5),
            ("Jackets", 6, 7),
            ("Dresses", 11, 16),
            ("Skirts", 17, 18),
            ("Blouses", 21, 22),
            ("Evening Gowns", 12, 13),
            ("Sun Dresses", 14, 15),
            ("new item", 19, 20),
        ]

        self.assertEqual(new_node.get_position(), (3, 4))
        self.assertCountEqual(actual_values, expected_values)

    def test_move_item_default(self):
        new_parent = MenuItem.objects.get(name="Men's")
        node = MenuItem.objects.get(name="Dresses")
        node.parent = new_parent

        node.save()

        actual_values = self._get_tree_values()
        expected_values = [
            ("Clothing", 1, 22),
            ("Men's", 2, 15),
            ("Women's", 16, 21),
            ("Suits", 3, 8),
            ("Slacks", 4, 5),
            ("Jackets", 6, 7),
            ("Dresses", 9, 14),
            ("Skirts", 17, 18),
            ("Blouses", 19, 20),
            ("Evening Gowns", 10, 11),
            ("Sun Dresses", 12, 13),
        ]

        self.assertCountEqual(actual_values, expected_values)
        self.assertEqual(node.get_position(), (2, 2))

    def test_move_item_positioned(self):
        new_parent = MenuItem.objects.get(name="Men's")
        node = MenuItem.objects.get(name="Dresses")
        node.parent = new_parent
        node.set_new_position(0)

        node.save()

        actual_values = self._get_tree_values()
        expected_values = [
            ("Clothing", 1, 22),
            ("Men's", 2, 15),
            ("Women's", 16, 21),
            ("Suits", 9, 14),
            ("Slacks", 10, 11),
            ("Jackets", 12, 13),
            ("Dresses", 3, 8),
            ("Skirts", 17, 18),
            ("Blouses", 19, 20),
            ("Evening Gowns", 4, 5),
            ("Sun Dresses", 6, 7),
        ]

        self.assertCountEqual(actual_values, expected_values)
        self.assertEqual(node.get_position(), (1, 2))

    def test_change_siblings_order(self):
        node = MenuItem.objects.get(name="Dresses")
        node.set_new_position(-1)

        node.save()

        actual_values = self._get_tree_values()
        expected_values = [
            ("Clothing", 1, 22),
            ("Men's", 2, 9),
            ("Women's", 10, 21),
            ("Suits", 3, 8),
            ("Slacks", 4, 5),
            ("Jackets", 6, 7),
            ("Dresses", 15, 20),
            ("Skirts", 11, 12),
            ("Blouses", 13, 14),
            ("Evening Gowns", 16, 17),
            ("Sun Dresses", 18, 19),
        ]

        self.assertCountEqual(actual_values, expected_values)
        self.assertEqual(node.get_position(), (3, 3))

    def test_change_name(self):
        node = MenuItem.objects.get(name="Skirts")
        node.name = "Pants"
        node.save()

        actual_values = self._get_tree_values()
        expected_values = [
            ("Clothing", 1, 22),
            ("Men's", 2, 9),
            ("Women's", 10, 21),
            ("Suits", 3, 8),
            ("Slacks", 4, 5),
            ("Jackets", 6, 7),
            ("Dresses", 11, 16),
            ("Pants", 17, 18),
            ("Blouses", 19, 20),
            ("Evening Gowns", 12, 13),
            ("Sun Dresses", 14, 15),
        ]

        self.assertCountEqual(actual_values, expected_values)

    def test_delete_model(self):
        node = MenuItem.objects.get(name="Dresses")
        node.delete()

        actual_values = self._get_tree_values()
        expected_values = [
            ("Clothing", 1, 16),
            ("Men's", 2, 9),
            ("Women's", 10, 15),
            ("Suits", 3, 8),
            ("Slacks", 4, 5),
            ("Jackets", 6, 7),
            ("Skirts", 11, 12),
            ("Blouses", 13, 14),
        ]

        self.assertCountEqual(actual_values, expected_values)

        node = MenuItem.objects.get(name="Blouses")
        node.delete()

        actual_values = self._get_tree_values()
        expected_values = [
            ("Clothing", 1, 14),
            ("Men's", 2, 9),
            ("Women's", 10, 13),
            ("Suits", 3, 8),
            ("Slacks", 4, 5),
            ("Jackets", 6, 7),
            ("Skirts", 11, 12),
        ]

        self.assertCountEqual(actual_values, expected_values)


class TestMenuItemModelWithBlankDb(TestCase):
    def test_create_new_root(self):
        new_root = MenuItem(name="new root", lft=0, rgt=0)
        new_root.save()

        self.assertEqual(new_root.lft, 1)
        self.assertEqual(new_root.rgt, 2)
