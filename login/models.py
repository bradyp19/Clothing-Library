from django.db import models
from django.contrib.auth.models import User

# classes for patron and librarian.

class Patron(models.Model):
    patron = models.OneToOneField(User, on_delete=models.CASCADE)
    def __str__(self):
        return f'{self.user.email} Patron Profile'

class Librarian(models.Model):
    librarian = models.OneToOneField(User, on_delete=models.CASCADE)
    def __str__(self):
        return f'{self.user.email} Librarian Profile'
