from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views import View
from django.contrib.auth.decorators import login_required

class LoginView(View):
    template_name = "closet/login.html"

    def get(self, request, *args, **kwargs):  # Add GET request handling
        return render(request, self.template_name)

@login_required
def dashboard(request):
    return render(request, "closet/dashboard.html", {"user": request.user})
