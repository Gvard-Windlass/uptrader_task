from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from menu_maker.models import MenuItem
from menu_maker.admin import MenuAdmin


class TestMenuAdminModelWithFixtures(TestCase):
    fixtures = ["menu_maker.json"]

    def _get_tree_values(self):
        return MenuItem.objects.order_by("id").values_list("name", "lft", "rgt")

    def setUp(self) -> None:
        self.admin_model = MenuAdmin(model=MenuItem, admin_site=AdminSite())

    def test_create_new_root(self):
        new_root = MenuItem(name="new root", lft=0, rgt=0)
        self.admin_model.save_model(obj=new_root, request=None, form=None, change=None)

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

    def test_add_child_item(self):
        parent_node = MenuItem.objects.get(id=3)
        new_node = MenuItem(name="new item", lft=0, rgt=0, parent=parent_node)
        self.admin_model.save_model(obj=new_node, request=None, form=None, change=None)

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

    def test_move_item(self):
        new_parent = MenuItem.objects.get(id=2)
        node = MenuItem.objects.get(id=7)
        node.parent = new_parent
        self.admin_model.save_model(obj=node, request=None, form=None, change=None)

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


class TestMenuAdminModel(TestCase):
    def setUp(self) -> None:
        self.admin_model = MenuAdmin(model=MenuItem, admin_site=AdminSite())

    def test_create_new_root(self):
        new_root = MenuItem(name="new root", lft=0, rgt=0)
        self.admin_model.save_model(obj=new_root, request=None, form=None, change=None)

        self.assertEqual(new_root.lft, 1)
        self.assertEqual(new_root.rgt, 2)
