import django_filters
from .models import Item, Clothing, Shoes

class ItemFilter(django_filters.FilterSet):
    class Meta:
        model = Item
        fields = ['condition', 'fit', 'occasion','gender']