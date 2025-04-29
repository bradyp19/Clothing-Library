from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta 

class Item(models.Model):
    item_name = models.CharField(max_length=60)
    brand = models.CharField(max_length=60)

    STATUS_CHOICES = [
        ('OUT', 'Checked Out'),
        ('IN', 'Checked In'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='IN')
    description = models.TextField(blank=True, null=True)

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
    in_collection = models.BooleanField(default=False)
    in_private_collection = models.BooleanField(default=False)

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

class Images(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='closet_items/')
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

# New Collection model
class Collection(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collections')
    # Allow a collection to include many items (and vice versa)
    items = models.ManyToManyField(Item, related_name='collections', blank=True) #related_name is used in querying so collections instead of collection_set
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    access_list = models.ManyToManyField(User, related_name='access_list', blank=True) #when collection is created, all librarians + owner should be added to access_list

    PRIVACY_CHOICES = [
        ("PRIVATE", "Private"),
        ("PUBLIC", "Public"),
    ]

    privacy_setting = models.CharField(max_length=10, choices=PRIVACY_CHOICES, default='PUBLIC')

    def __str__(self):
        return self.name
    
class BorrowRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('DENIED', 'Denied'),
    ]
    # Each borrow request is tied to an item and a requester (User)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="borrow_requests")
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name="borrow_requests")
    request_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    comment = models.TextField(blank=True, null=True)  # Optional comment from requester
    updated_at = models.DateTimeField(auto_now=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=lambda: timezone.now() + timedelta(days=7)) # default lending period is 1 week
    extension_requested = models.BooleanField(default=False)
    extended_date = models.DateTimeField(null=True, blank=True)
    extension_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"{self.item.item_name} requested by {self.requester.username} ({self.status})"

class AccessRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('DENIED', 'Denied'),
    ]
    # Each borrow request is tied to a collection and a requester (User)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name="access_requests")
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name="access_requests")
    request_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    comment = models.TextField(blank=True, null=True)  # Optional comment from requester
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.collection.name} requested by {self.requester.username} ({self.status})"

class ItemReview(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]  # 1-5 stars
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="reviews")
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="item_reviews")
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.item.item_name} - {self.reviewer.username} ({self.rating} stars)"