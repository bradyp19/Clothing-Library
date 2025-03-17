from django.db import models
from django.contrib.auth.models import User

# classes for patron and librarian.

def profile_picture_path(instance, filename):
    # This can customize the path where the file is stored, e.g.:
    return f"profile_pics/user_{instance.user.id}/{filename}"

class Profile(models.Model):
    ROLE_CHOICES = [
        ('patron', 'Patron'),
        ('librarian', 'Librarian'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, blank=True)
    profile_picture = models.ImageField(
        upload_to=profile_picture_path,
        default='profile_pics/hotel.jpg',  # permanent default
        blank=False,
        null=False
    )

    # Add more fields if needed, e.g. phone, address, etc.

    @property
    def is_complete(self):
        # Simple check: consider 'role' as required. 
        # Expand this if you have more required fields.
        return bool(self.role) and bool(self.profile_picture)
    

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
