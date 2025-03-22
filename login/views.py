from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect
from django.views import View, generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.urls import reverse
from django.views.generic.list import ListView

from .models import Librarian, Patron, Profile
from .forms import LoginForm, ProfileForm        


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
                # Check the user's profile completeness
                profile, created = Profile.objects.get_or_create(user=user)
                if not profile.is_complete:
                    return redirect("login:profile_setup")
                # If complete, send to dashboard (or whichever page you prefer)
                return redirect("dashboard")
        return render(request, self.template_name, {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login:login")


@login_required #Old, not need anymore
def dashboard(request):
    return render(request, "login/dashboard.html", {"user": request.user}) 


@login_required
def profile_setup_view(request):
    # Get or create the user's Profile
    profile, created = Profile.objects.get_or_create(user=request.user)

    # If the profile is already complete, go straight to the dashboard
    if profile.is_complete:
        if profile.role == 'patron':
            return redirect('login:patron_dashboard')
        else:
            return redirect('login:librarian_dashboard')

    # Otherwise, show the form
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            # Redirect based on the chosen role
            if profile.role == 'patron':
                return redirect('login:patron_dashboard')
            else:
                return redirect('login:librarian_dashboard')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'login/profile_setup.html', {'form': form})


@login_required
def profile_edit_view(request):
    profile = request.user.profile  # Assuming you always have a Profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            # Redirect to the appropriate dashboard
            if profile.role == 'patron':
                return redirect('login:patron_dashboard')
            else:
                return redirect('login:librarian_dashboard')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'login/profile_edit.html', {'form': form})

@login_required
def patron_dashboard_view(request):
    return render(request, 'login/patron_dashboard.html')

@login_required
def librarian_dashboard_view(request):
    return render(request, 'login/librarian_dashboard.html')
