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
                descendants = MenuItem.objects.get_descendants(
                    obj.parent.id, direct_only=True
                )
                # TODO make dynamic
                position = len(descendants)

                if position == 0 or not descendants:
                    boundary = obj.parent.lft
                else:
                    boundary = descendants[position - 1].rgt

                MenuItem.objects.filter(lft__gt=boundary).update(lft=F("lft") + 2)
                MenuItem.objects.filter(rgt__gt=boundary).update(rgt=F("rgt") + 2)
            else:  # new root
                boundary = MenuItem.objects.aggregate(Max("rgt"))["rgt__max"] or 0

            obj.lft = boundary + 1
            obj.rgt = boundary + 2

        return super().save_model(request, obj, form, change)
