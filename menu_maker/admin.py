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
                self._create_new_child_node(obj, position)
            else:  # new root
                boundary = MenuItem.objects.aggregate(Max("rgt"))["rgt__max"] or 0
                obj.lft = boundary + 1
                obj.rgt = boundary + 2
        else:  # update
            old_obj = MenuItem.objects.get(id=obj.id)
            old_pos = old_obj.get_position()
            # move node under new parent if changed
            if obj.parent_id != old_obj.parent_id or old_pos and old_pos[0] != position:
                self._update_node_position(obj, position)

        return super().save_model(request, obj, form, change)

    def delete_model(self, request, obj: MenuItem):
        width = obj.rgt - obj.lft + 1
        MenuItem.objects.filter(lft__range=(obj.lft, obj.rgt)).delete()
        MenuItem.objects.filter(lft__gt=obj.rgt).update(lft=F("lft") - width)
        MenuItem.objects.filter(rgt__gt=obj.rgt).update(rgt=F("rgt") - width)

        return super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        queryset = queryset.order_by("lft")
        for query in queryset:
            persists = MenuItem.objects.filter(id=query.id).first()
            if persists:
                self.delete_model(request, persists)

    def _create_new_child_node(self, obj: MenuItem, position: int):
        descendants = MenuItem.objects.get_descendants(obj.parent_id, direct_only=True)

        if position == -1 or position > len(descendants):
            position = len(descendants)

        # no children or insert as first child
        if position == 0 or not descendants:
            boundary = obj.parent.lft
        else:
            boundary = descendants[position - 1].rgt

        MenuItem.objects.filter(rgt__gt=boundary).update(rgt=F("rgt") + 2)
        MenuItem.objects.filter(lft__gt=boundary).update(lft=F("lft") + 2)

        obj.lft = boundary + 1
        obj.rgt = boundary + 2

    def _update_node_position(self, obj: MenuItem, position: int):
        tree_ids = list(MenuItem.objects.get_tree(obj.id).values_list("id", flat=True))

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
