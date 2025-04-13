import django_filters
from .models import Item, Clothing, Shoes, Collection


class ItemFilter(django_filters.FilterSet):
    class Meta:
        model = Item
        fields = ['condition', 'fit', 'occasion','gender', 'status']

class CollectionFilter(django_filters.FilterSet):
    class Meta:
        model = Collection
        fields = ['privacy_setting']