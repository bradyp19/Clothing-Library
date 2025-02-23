from django.urls import path
from . import views


app_name = "closet"
urlpatterns = [
    #path("", views.LoginView.as_view(), name="login"),
    path("dashboard", views.dashboard, name="dashboard"),  # Ensure dashboard exists
    path("add/", views.AddView.as_view(), name="add"),
    path("patron_list/", views.PatronView.as_view(), name="patron"),
    path("librarian_list/", views.LibrarianView.as_view(), name="librarian")
]