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

    def test_delete_selection(self):
        selection = MenuItem.objects.filter(name__in=["Dresses", "Skirts", "Blouses"])
        self.admin_model.delete_queryset(request=None, queryset=selection)

        actual_values = self._get_tree_values()
        expected_values = [
            ("Clothing", 1, 12),
            ("Men's", 2, 9),
            ("Women's", 10, 11),
            ("Suits", 3, 8),
            ("Slacks", 4, 5),
            ("Jackets", 6, 7),
        ]

        self.assertCountEqual(actual_values, expected_values)
