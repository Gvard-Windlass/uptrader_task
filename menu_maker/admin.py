from typing import Any
from django.db.models import F, Max
from django.contrib import admin
from menu_maker.forms import MenuItemForm
from menu_maker.models import MenuItem


@admin.register(MenuItem)
class MenuAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "child_position")
    search_fields = ("name", "parent__name")
    exclude = ("lft", "rgt")
    form = MenuItemForm

    def child_position(self, obj: MenuItem):
        values = obj.get_position()
        if values:
            position, total = values
            return f"{position}/{total}"

    def save_model(
        self, request: Any, obj: MenuItem, form: MenuItemForm, change: Any
    ) -> None:
        if form.is_valid():
            position = form.cleaned_data["position"]

        if not obj.id:  # create
            if obj.parent:  # new node
                descendants = MenuItem.objects.get_descendants(
                    obj.parent_id, direct_only=True
                )

                if position == -1 or position > len(descendants):
                    position = len(descendants)

                # no children or insert as first child
                if position == 0 or not descendants:
                    boundary = obj.parent.lft
                else:
                    boundary = descendants[position - 1].rgt

                MenuItem.objects.filter(rgt__gt=boundary).update(rgt=F("rgt") + 2)
                MenuItem.objects.filter(lft__gt=boundary).update(lft=F("lft") + 2)
            else:  # new root
                boundary = MenuItem.objects.aggregate(Max("rgt"))["rgt__max"] or 0

            obj.lft = boundary + 1
            obj.rgt = boundary + 2
        else:  # update
            # move node under new parent if changed
            if obj.parent_id != MenuItem.objects.get(pk=obj.id).parent_id:
                tree_ids = list(
                    MenuItem.objects.get_tree(obj.id).values_list("id", flat=True)
                )

                # update previous obj place
                offset = obj.rgt - obj.lft + 1
                source_boundary = obj.lft

                MenuItem.objects.filter(lft__gt=source_boundary).exclude(
                    id__in=tree_ids
                ).update(lft=F("lft") - offset)

                MenuItem.objects.filter(rgt__gt=source_boundary).exclude(
                    id__in=tree_ids
                ).update(rgt=F("rgt") - offset)

                # update new obj place

                target_descendants = MenuItem.objects.get_descendants(
                    obj.parent_id, direct_only=True
                )

                if position == -1 or position > len(target_descendants):
                    position = len(target_descendants)

                # target has no children or insert as first child
                if position == 0 or not target_descendants:
                    target_boundary = obj.parent.lft
                else:
                    target_boundary = target_descendants[position - 1].rgt

                MenuItem.objects.filter(rgt__gt=target_boundary).exclude(
                    id__in=tree_ids
                ).update(rgt=F("rgt") + offset)

                MenuItem.objects.filter(lft__gt=target_boundary).exclude(
                    id__in=tree_ids
                ).update(lft=F("lft") + offset)

                # update inserted tree
                shift = target_boundary - source_boundary + 1

                MenuItem.objects.filter(id__in=tree_ids).update(
                    lft=F("lft") + shift, rgt=F("rgt") + shift
                )

                # does not update through above query?
                obj.lft += shift
                obj.rgt += shift

        return super().save_model(request, obj, form, change)
