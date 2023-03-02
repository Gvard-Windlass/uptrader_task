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

    def delete_queryset(self, request, queryset):
        queryset = queryset.order_by("lft")
        for query in queryset:
            persists = MenuItem.objects.filter(id=query.id).first()
            if persists:
                persists.delete()
