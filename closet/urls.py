from django.urls import path
from . import views

app_name = "closet"
urlpatterns = [
    path("", views.item_list, name="closet_index"),
    path("<int:item_id>/", views.item_detail, name="item_detail"),

    path("add/", views.AddView.as_view(), name="add"), # Add item
    path("edit_item/<int:item_id>/", views.edit_item, name="edit_item"),
    path("delete_item/<int:item_id>/", views.delete_item, name="delete_item"),
    
    path("collections/", views.collections_list, name = "collections_list"),
    path("public_collections/", views.public_collection_list, name="public_collections"),
    path("my_collections", views.my_collections_list, name = "my_collections"),

    path("add_collection/", views.add_collection, name="add_collection"),
    path("collections_list/<int:collection_id>/", views.collection_detail, name = "collection_detail"),
    path("edit_collection/<int:collection_id>/", views.edit_collection, name = "edit_collection"),
    path("delete_collection/<int:collection_id>/", views.delete_collection, name = "delete_collection"),

    path("collections/<int:collection_id>/access/", views.request_access_collection, name = "request_access_collection"),
    path("access_requests/", views.review_access_requests, name = "review_access_requests"),
    path("access_requests/<int:request_id>/<str:action>/", views.update_access_request, name = "update_access_request"),

    path("item/<int:item_id>/borrow/", views.request_borrow_item, name="request_borrow_item"),
    path('borrow_request/<int:request_id>/return/', views.return_borrowed_item, name='return_borrowed_item'),
    path("my_borrow_requests/", views.my_borrow_requests, name="my_borrow_requests"),
    path("review_borrow_requests/", views.review_borrow_requests, name="review_borrow_requests"),
    path("borrow_request/<int:request_id>/<str:action>/", views.update_borrow_request, name="update_borrow_request"),
]
