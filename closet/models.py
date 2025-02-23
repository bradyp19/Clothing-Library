from django.db import models
from django.contrib.auth.models import AbstractUser

class Item(models.Model):
    item_name = models.CharField(max_length=60)
    brand = models.CharField(max_length=60)

    CONDITION_CHOICES = [
        ("NWT", "New with Tags"),
        ("NWOT", "New without Tags"),
        ("LN", "Like New"),
        ("VGUC", "Very Good"),
        ("GUC", "Good"),
        ("DUC", "Distressed"),
    ]
    condition = models.CharField(max_length=4, choices=CONDITION_CHOICES)

    FIT_CHOICES = [
        ("TF", "Tight fit"),
        ("TTS", "True to size"),
        ("RF", "Relaxed fit"),
    ]
    fit = models.CharField(max_length=3, choices=FIT_CHOICES)

    OCCASION_CHOICES = [
        ("CASUAL", "Casual"),
        ("BUSINESS", "Business"),
        ("FORMAL", "Formal"),
        ("THEMED", "Themed"),
    ]
    occasion = models.CharField(max_length=8, choices=OCCASION_CHOICES)

    GENDER_CHOICES = [
        ("M", "Men"),
        ("W", "Women"),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

class Clothing(Item):
    SIZE_CHOICES = [
        ("XXS", "Double Extra Small"),
        ("XS", "Extra Small"),
        ("S", "Small"),
        ("M", "Medium"),
        ("L", "Large"),
        ("XL", "Extra Large"),
        ("XXL", "Double Extra Large"),
    ]
    size = models.CharField(max_length=3, choices=SIZE_CHOICES)

    CLOTHING_TYPE_CHOICES = [
        ("SHIRT", "Shirt"),
        ("PANTS", "Pants"),
        ("SKIRT", "Skirt"),
        ("DRESS", "Dress"),
        ("JACKET", "Jacket"),
        ("SWEATER", "Sweater"),
        ("SHORTS", "Shorts"),
        ("OTHER", "Other"),
    ]
    clothing_type = models.CharField(max_length=10, choices=CLOTHING_TYPE_CHOICES)

class Shoes(Item):
    SIZE_CHOICES = [
        ("5", "5"),
        ("5.5", "5.5"),
        ("6", "6"),
        ("6.5", "6.5"),
        ("7", "7"),
        ("7.5", "7.5"),
        ("8", "8"),
        ("8.5", "8.5"),
        ("9", "9"),
        ("9.5", "9.5"),
        ("10", "10"),
        ("10.5", "10.5"),
        ("11", "11"),
        ("11.5", "11.5"),
        ("12", "12"),
        ("12.5", "12.5"),
        ("13", "13"),
    ]
    size = models.CharField(max_length=4, choices=SIZE_CHOICES)

# classes for base user, patron, and librarian.

#class BaseUser(AbstractUser):
#    email = models.EmailField(max_length=20, unique=True)
#    name = models.CharField(max_length=120)

#class Patron(BaseUser):

#class Librarian(BaseUser):

