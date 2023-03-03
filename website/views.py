from django.views.generic.base import TemplateView
from django.shortcuts import get_object_or_404
from menu_maker.models import MenuItem


class HomeView(TemplateView):
    template_name = "website/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        menu_key = self.kwargs.get("menu_item_id")
        if menu_key:
            context["menu_item"] = get_object_or_404(MenuItem, pk=menu_key)
        return context
