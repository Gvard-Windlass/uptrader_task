from django.test import TestCase
from menu_maker.forms import MenuItemForm
from menu_maker.models import MenuItem


class TestMenuItemForm(TestCase):
    fixtures = ["menu_maker.json"]

    def test_valid_form(self):
        form_data = {
            "name": "new item",
            "parent": MenuItem.objects.get(id=1),
            "position": -1,
        }
        form = MenuItemForm(data=form_data)
        self.assertTrue(form.is_valid())
