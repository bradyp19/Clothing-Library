from django.urls import path
from . import views

urlpatterns = [
    path("", views.LoginView.as_view(), name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),  # Ensure dashboard exists
]