from django import forms
from menu_maker.models import MenuItem


class MenuItemForm(forms.ModelForm):
    position = forms.IntegerField(
        initial=-1,
        min_value=-1,
        help_text="0-based position amoung children, with -1 to insert last",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        position = self.instance.get_position()
        if position:
            self.fields["position"].initial = position[0] - 1

    def save(self, commit: bool = True):
        input_pos = self.cleaned_data["position"]
        self.instance.set_new_position(input_pos)
        return super().save(commit)

    class Meta:
        model = MenuItem
        exclude = ["lft", "rgt"]
