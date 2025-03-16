from django.urls import path
from .views import LoginView, logout_view, dashboard, patron_list, librarian_list


app_name = "login"
urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"), 
    path("dashboard/", dashboard, name="dashboard"),
    path("patrons/", patron_list, name="patron"),
    path("librarians/", librarian_list, name="librarian"),
]