from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect
from django.views import View, generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.urls import reverse
from django.views.generic.list import ListView

from .models import Item, Clothing, Shoes, Librarian, Patron
from .forms import ItemForm
from .forms import LoginForm

# class LoginView(View):
#     template_name = "closet/login.html"
    # def get(self, request, *args, **kwargs):  # Add GET request handling
    #     return render(request, self.template_name)

class LoginView(View):
    template_name = "closet/login.html"

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
    return redirect("login")

@login_required
def dashboard(request):
    return render(request, "closet/dashboard.html", {"user": request.user})

@login_required
class PatronView(ListView):
    model = Patron
    template_name = "closet/patron_list.html"

@login_required
class LibrarianView(ListView):
    model = Librarian
    template_name = "closet/librarian_list.html"