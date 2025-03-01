from django.urls import path
from . import views


app_name = "closet"
urlpatterns = [
    path("add/", views.AddView.as_view(), name="add"),
]