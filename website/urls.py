from django.urls import path
from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("clothing/<slug:slug>/", views.HomeView.as_view(), name="clothing"),
    path("electronics/<slug:slug>/", views.HomeView.as_view(), name="electronics"),
]
