from django.db import models
from django.contrib.auth.models import User

# classes for patron and librarian.

class Profile(models.Model):
    ROLE_CHOICES = [
        ('patron', 'Patron'),
        ('librarian', 'Librarian'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, blank=True)
    
    # Add more fields if needed, e.g. phone, address, etc.

    @property
    def is_complete(self):
        # Simple check: consider 'role' as required. 
        # Expand this if you have more required fields.
        return bool(self.role)
    

class Patron(models.Model):
    patron = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='patron_profile_pictures/', null=True, blank=True)
    def __str__(self):
        return f'{self.user.email} Patron Profile'

class Librarian(models.Model):
    librarian = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='librarian_profile_pictures/', null=True, blank=True)
    def __str__(self):
        return f'{self.user.email} Librarian Profile'
