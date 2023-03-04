from django.urls import path
from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("clothing/<int:menu_item_id>/", views.HomeView.as_view(), name="clothing"),
    path(
        "electronics/<int:menu_item_id>/", views.HomeView.as_view(), name="electronics"
    ),
]
