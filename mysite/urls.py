"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', RedirectView.as_view(url='/start/login/', permanent=False), name='home'),
    # comment the above line to show possible urls. Above line makes the page we go login page

    path("start/", include("login.urls")),  # Login, Dashboard, Patron, Librarian
    # path("", include("login.urls")),
    path("closet/", include("closet.urls")), # Closet App - Other features [ADD implemented now]

    path('accounts/logout/', auth_views.LogoutView.as_view(template_name='login/logout.html'), name='account_logout'),
    path('accounts/', include('allauth.urls')), # Google login

    # path('login/', auth_views.LoginView.as_view(template_name='login/login.html'), name='login'),
    # path('logout/', auth_views.LogoutView.as_view(template_name='login/logout.html'), name='logout'),
]
