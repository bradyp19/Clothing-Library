from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views import View

class LoginView(View):
    template_name = "closet/login.html"
