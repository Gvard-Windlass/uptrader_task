from typing import Any
from django.db.models import F, Max
from django.contrib import admin
from menu_maker.models import MenuItem


@admin.register(MenuItem)
class MenuAdmin(admin.ModelAdmin):
    list_display = ("name", "parent")
    search_fields = ("name", "parent__name")
    exclude = ("lft", "rgt")

    def save_model(self, request: Any, obj: MenuItem, form: Any, change: Any) -> None:
        if not obj.id:  # create
            if obj.parent:  # new node
                pass
            else:  # new root
                max_rgt = MenuItem.objects.aggregate(Max("rgt"))["rgt__max"] or 0
                obj.lft = max_rgt + 1
                obj.rgt = max_rgt + 2

        return super().save_model(request, obj, form, change)
