from django.urls import path
from . import views


app_name = "closet"
urlpatterns = [
    path("", views.item_list, name="closet_index"),
    path("<int:item_id>/", views.item_detail, name="item_detail"),
    path("add/", views.AddView.as_view(), name="add"),
]