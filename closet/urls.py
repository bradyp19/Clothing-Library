from django.urls import path
from . import views

app_name = "closet"
urlpatterns = [
    path("", views.item_list, name="closet_index"),
    path("<int:item_id>/", views.item_detail, name="item_detail"),
    path("add/", views.AddView.as_view(), name="add"),
    path("collections/", views.collections_list, name = "collections_list"),
    path("public_collections/", views.collections_list, name="public_collections"),
    path("my_collections", views.my_collections_list, name = "my_collections"),
    path("add_collection/", views.add_collection, name="add_collection"),
    path("collections_list/<int:collection_id>/", views.collection_detail, name = "collection_detail"),
    path("edit_collection/<int:collection_id>/", views.edit_collection, name = "edit_collection"),
    path("delete_collection/<int:collection_id>/", views.delete_collection, name = "delete_collection"),
]
