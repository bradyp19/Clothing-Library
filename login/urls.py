from django.urls import path
from .views import (
    LoginView, 
    logout_view, 
    dashboard,
    profile_setup_view,
    profile_edit_view,
    patron_dashboard_view,
    librarian_dashboard_view
)

app_name = "login"
urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),     
    
    path('profile-setup/', profile_setup_view, name='profile_setup'),

    path("dashboard/", dashboard, name="dashboard"),

    path('profile/edit/', profile_edit_view, name='profile_edit'),
    path('dashboard/patron/', patron_dashboard_view, name='patron_dashboard'),
    path('dashboard/librarian/', librarian_dashboard_view, name='librarian_dashboard'),
]
