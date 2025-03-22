from django import forms
from .models import Profile


# class ProfileForm(forms.ModelForm):
#     class Meta:
#         model = Profile
#         fields = ['role', 'profile_picture']  # Add other fields if you have them

class PatronProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        # Exclude the role field so patrons cannot change it.
        fields = ['profile_picture']  # Add any other fields you want patrons to edit

class LibrarianProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        # Include role here so a librarian can downgrade to patron if desired.
        fields = ['role', 'profile_picture']

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)