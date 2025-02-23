from django.urls import path
from . import views


app_name = "closet"
urlpatterns = [
    #path("", views.LoginView.as_view(), name="login"),
    path("", views.dashboard, name="dashboard"),  # Ensure dashboard exists
    path("add/", views.AddView.as_view(), name="add"),
    path("patron/", views.PatronView.as_view()),
    path("librarian/", views.LibrarianView.as_view())
]