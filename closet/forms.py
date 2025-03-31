from django import forms  # Import your custom widget
from .models import Item, Clothing, Shoes, Images, Collection

class ItemForm(forms.ModelForm):
    ITEM_TYPE_CHOICES = [
        ("CLOTHING", "Clothing"),
        ("SHOES", "Shoes"),
    ]
    item_type = forms.ChoiceField(choices=ITEM_TYPE_CHOICES, widget=forms.Select(attrs={"id": "item-type"}))
    class Meta:
        model = Item
        fields = ["item_name", "brand", "condition", "fit", "occasion", "gender",]

    clothing_size = forms.ChoiceField(choices=Clothing.SIZE_CHOICES, required=False, widget=forms.Select(attrs={"id": "clothing-size"}))
    clothing_type = forms.ChoiceField(choices=Clothing.CLOTHING_TYPE_CHOICES, required=False, widget=forms.Select(attrs={"id": "clothing-type"}))
    shoes_size = forms.ChoiceField(choices=Shoes.SIZE_CHOICES, required=False, widget=forms.Select(attrs={"id": "shoes-size"}))

class ImageForm(forms.ModelForm):
    class Meta:
        model = Images
        fields = ["image"]

class CustomMMCF(forms.ModelMultipleChoiceField):
    def label_from_instance(self, item):
        return '%s' % item.item_name

class CollectionFormPatron(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['name', 'description','items'] #no option for privacy setting, so default will be saved
    items = CustomMMCF(
        queryset=Item.objects.all(),
        widget=forms.CheckboxSelectMultiple()
    )

class CollectionFormLibrarian(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['name', 'description', 'privacy_setting', 'items']
    items = CustomMMCF(
        queryset=Item.objects.all(),
        widget=forms.CheckboxSelectMultiple()
    )

AddImageFormset = forms.inlineformset_factory(Item, Images, extra=3, form=ImageForm, can_delete=False)

def get_wanted_items_queryset(option):
    if option == 1:
        return Item.objects.all()
    elif option == 2: # get only objects that are not in a collection
        return Item.objects.filter(collections=None)
    elif option == 3: # get only objects that are not in a private collection
        wanted_items = set()
        for item in Item.objects.all():
            if not check_for_private(item):
                wanted_items.add(item.id)
        return Item.objects.filter(id__in=wanted_items)

def check_for_private(item):
    count = item.collections.count() # number of collections that an item is part of
    if count > 1 or count == 0: # if it's in more than 1 collection, none of them should be private. if not in collection, can't be in a private collection
        return False
    return item.collections.first().privacy_setting.lower() == 'private' # otherwise, check if that 1 collection is private
