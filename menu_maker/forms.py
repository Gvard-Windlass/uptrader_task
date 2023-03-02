from django import forms
from menu_maker.models import MenuItem


class MenuItemForm(forms.ModelForm):
    position = forms.IntegerField(initial=-1, min_value=-1)

    class Meta:
        model = MenuItem
        exclude = ["lft", "rgt"]
