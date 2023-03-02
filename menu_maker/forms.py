from django import forms
from menu_maker.models import MenuItem


class MenuItemForm(forms.ModelForm):
    position = forms.IntegerField(
        initial=-1,
        min_value=-1,
        help_text="0-based position amoung children, with -1 to insert last",
    )

    class Meta:
        model = MenuItem
        exclude = ["lft", "rgt"]
