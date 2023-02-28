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


class TestMenuAdminModel(TestCase):
    def setUp(self) -> None:
        self.admin_model = MenuAdmin(model=MenuItem, admin_site=AdminSite())

    def test_create_new_root(self):
        new_root = MenuItem(name="new root", lft=0, rgt=0)
        self.admin_model.save_model(obj=new_root, request=None, form=None, change=None)
        self.assertEqual(new_root.lft, 1)
        self.assertEqual(new_root.rgt, 2)
