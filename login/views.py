from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.views import View, generic
from django.contrib.auth.decorators import login_required, user_passes_test
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
    profile, created = Profile.objects.get_or_create(user=request.user)

    # If the profile is already complete, go straight to the dashboard
    if profile.is_complete:
        if profile.role == 'patron':
            return redirect('login:patron_dashboard')
        else:
            return redirect('login:librarian_dashboard')

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            instance = form.save(commit=False)
            # Force the role to 'patron' unless the user is already a librarian
            if request.user.profile.role != 'librarian':
                instance.role = 'patron'
            instance.save()
            # Redirect based on the final role
            if instance.role == 'patron':
                return redirect('login:patron_dashboard')
            else:
                return redirect('login:librarian_dashboard')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'login/profile_setup.html', {'form': form})


@login_required
def profile_edit_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            instance = form.save(commit=False)
            # Force the role to 'patron' unless the user is already a librarian
            if request.user.profile.role != 'librarian':
                instance.role = 'patron'
            instance.save()
            # Redirect to the appropriate dashboard
            if instance.role == 'patron':
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


def librarian_required(view_func):
    return user_passes_test(
        lambda u: hasattr(u, 'profile') and u.profile.role == 'librarian',
        login_url='login:login'
    )(view_func)

@login_required
@librarian_required
def list_patrons(request):
    from .models import Profile
    patrons = Profile.objects.filter(role='patron')
    return render(request, 'login/list_patrons.html', {'patrons': patrons})

@login_required
@librarian_required
def upgrade_patron(request, patron_id):
    patron_profile = get_object_or_404(Profile, pk=patron_id, role='patron')
    if request.method == 'POST':
        # If confirmed, set their role to librarian
        patron_profile.role = 'librarian'
        patron_profile.save()
        return redirect('login:list_patrons')
    # Otherwise, show a simple confirmation page
    return render(request, 'login/upgrade_confirmation.html', {'profile': patron_profile})