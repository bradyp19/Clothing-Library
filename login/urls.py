from django.urls import path
from . import views, LoginView, logout_view

app_name = "login"
urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),  # Moved here
    path("patrons/", views.patron_list, name="patron_list"),  # Moved here
    path("librarians/", views.librarian_list, name="librarian_list"),  # Moved here
]