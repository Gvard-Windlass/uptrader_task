from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from menu_maker.models import MenuItem
from menu_maker.admin import MenuAdmin


class TestMenuAdminModelWithFixtures(TestCase):
    fixtures = ["menu_maker.json"]

    def setUp(self) -> None:
        self.admin_model = MenuAdmin(model=MenuItem, admin_site=AdminSite())

    def test_create_new_root(self):
        new_root = MenuItem(name="new root", lft=0, rgt=0)
        self.admin_model.save_model(obj=new_root, request=None, form=None, change=None)

        self.assertEqual(new_root.lft, 23)
        self.assertEqual(new_root.rgt, 24)

    def test_add_child_item(self):
        parent_node = MenuItem.objects.get(id=3)
        new_node = MenuItem(name="new item", lft=0, rgt=0, parent=parent_node)
        self.admin_model.save_model(obj=new_node, request=None, form=None, change=None)

        self.assertEqual(new_node.lft, 21)
        self.assertEqual(new_node.rgt, 22)

        parent_node.refresh_from_db()
        self.assertEqual(parent_node.lft, 10)
        self.assertEqual(parent_node.rgt, 23)

        root_node = MenuItem.objects.get(id=1)
        self.assertEqual(root_node.lft, 1)
        self.assertEqual(root_node.rgt, 24)


class TestMenuAdminModel(TestCase):
    def setUp(self) -> None:
        self.admin_model = MenuAdmin(model=MenuItem, admin_site=AdminSite())

    def test_create_new_root(self):
        new_root = MenuItem(name="new root", lft=0, rgt=0)
        self.admin_model.save_model(obj=new_root, request=None, form=None, change=None)

        self.assertEqual(new_root.lft, 1)
        self.assertEqual(new_root.rgt, 2)
