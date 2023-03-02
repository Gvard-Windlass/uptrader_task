from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from menu_maker.forms import MenuItemForm
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
        form_data = {
            "name": new_root.name,
            "position": -1,
        }
        form = MenuItemForm(data=form_data)
        self.assertTrue(form.is_valid())

        self.admin_model.save_model(obj=new_root, request=None, form=form, change=None)

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
        form_data = {
            "name": new_node.name,
            "parent": new_node.parent_id,
            "position": -1,
        }
        form = MenuItemForm(data=form_data)
        self.assertTrue(form.is_valid())

        self.admin_model.save_model(obj=new_node, request=None, form=form, change=None)

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
        form_data = {
            "name": new_node.name,
            "parent": new_node.parent_id,
            "position": 2,
        }
        form = MenuItemForm(data=form_data)
        self.assertTrue(form.is_valid())

        self.admin_model.save_model(obj=new_node, request=None, form=form, change=None)

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
        form_data = {
            "name": node.name,
            "parent": node.parent_id,
            "position": -1,
        }
        form = MenuItemForm(data=form_data)
        self.assertTrue(form.is_valid())

        self.admin_model.save_model(obj=node, request=None, form=form, change=None)

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
        form_data = {
            "name": node.name,
            "parent": node.parent_id,
            "position": 0,
        }
        form = MenuItemForm(data=form_data)
        self.assertTrue(form.is_valid())

        self.admin_model.save_model(obj=node, request=None, form=form, change=None)

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


class TestMenuAdminModel(TestCase):
    def setUp(self) -> None:
        self.admin_model = MenuAdmin(model=MenuItem, admin_site=AdminSite())

    def test_create_new_root(self):
        new_root = MenuItem(name="new root", lft=0, rgt=0)
        form_data = {
            "name": new_root.name,
            "position": -1,
        }
        form = MenuItemForm(data=form_data)
        self.assertTrue(form.is_valid())

        self.admin_model.save_model(obj=new_root, request=None, form=form, change=None)

        self.assertEqual(new_root.lft, 1)
        self.assertEqual(new_root.rgt, 2)
