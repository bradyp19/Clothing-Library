from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect
from django.views import View, generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.urls import reverse
from django.views.generic.list import ListView

from .models import Librarian, Patron
from .forms import LoginForm         

# class LoginView(View):
#     template_name = "closet/login.html"
    # def get(self, request, *args, **kwargs):  # Add GET request handling
    #     return render(request, self.template_name)

class LoginView(View):
    template_name = "login/login.html"

    def get(self, request):
        form = LoginForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect("dashboard")
        return render(request, self.template_name, {"form": form})

def logout_view(request):
    logout(request)
    return redirect("login:login")

@login_required
def dashboard(request):
    return render(request, "login/dashboard.html", {"user": request.user}) 

@login_required
def patron_list(request):
    patrons = Patron.objects.all()
    return render(request, "login/patron_list.html", {"patrons": patrons})

@login_required
def librarian_list(request):
    librarians = Librarian.objects.all()
    return render(request, "login/librarian_list.html", {"librarians": librarians})