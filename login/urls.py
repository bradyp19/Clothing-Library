from django.contrib import admin
from django.urls import path
from .views import (
    LoginView, logout_view, dashboard, profile_setup_view,
    patron_profile_edit_view, librarian_profile_edit_view,
    patron_dashboard_view, librarian_dashboard_view,
    list_patrons, upgrade_patron, anon_dashboard_view
)

app_name = "login"
urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("admin/", admin.site.urls, name="admin"),    

    path("dashboard/", dashboard, name="dashboard"),

    path('profile-setup/', profile_setup_view, name='profile_setup'),
    path('profile/edit/patron/', patron_profile_edit_view, name='patron_profile_edit'),
    path('profile/edit/librarian/', librarian_profile_edit_view, name='librarian_profile_edit'),
    
    path('dashboard/patron/', patron_dashboard_view, name='patron_dashboard'),
    path('dashboard/librarian/', librarian_dashboard_view, name='librarian_dashboard'),
    path('dashboard/anon/', anon_dashboard_view, name='anon_dashboard'),
   
    # Existing librarian upgrade URLs, if needed:
    path('patrons/', list_patrons, name='list_patrons'),
    path('upgrade/<int:patron_id>/', upgrade_patron, name='upgrade_patron'),
]