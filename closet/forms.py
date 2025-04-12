from django import forms  # Import your custom widget
from .models import Item, Clothing, Shoes, Images, Collection, BorrowRequest

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

def get_wanted_items_queryset(option):
    if option == 'all':
        return Item.objects.all()
    elif option == 'private': # get only objects that are not in a collection - use for PRIVATE collections
        return Item.objects.filter(collections=None)
    elif option == 'public': # get only objects that are not in a private collection - use for PUBLIC collections
        wanted_items = set()
        for item in Item.objects.all():
            if not in_private(item):
                wanted_items.add(item.id)
        return Item.objects.filter(id__in=wanted_items)

def in_private(item):
    count = item.collections.count() # number of collections that an item is part of
    if count > 1 or count == 0: # if it's in more than 1 collection, none of them should be private. if not in collection, can't be in a private collection
        return False
    return item.collections.first().privacy_setting.lower() == 'private' # otherwise, check if that 1 collection is private

class CustomMMCF(forms.ModelMultipleChoiceField):
    def label_from_instance(self, item):
        return '%s' % item.item_name

class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['name', 'description','items'] #no option for privacy setting, so default will be saved
    items = CustomMMCF(
        queryset=Item.objects.none(),  # Set an empty queryset initially
        widget=forms.CheckboxSelectMultiple()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['items'].queryset = get_wanted_items_queryset('public')  # since patrons can only select public setting

class CollectionFormPrivacy(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['name', 'description', 'privacy_setting', 'items']
    items = CustomMMCF(
        queryset=Item.objects.all(),
        widget=forms.CheckboxSelectMultiple()
    )

AddImageFormset = forms.inlineformset_factory(Item, Images, extra=3, form=ImageForm, can_delete=False)

class BorrowRequestForm(forms.ModelForm):
    class Meta:
        model = BorrowRequest
        fields = ['comment']  # Let users optionally add a comment with their request
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Optional: Add a note...'}),
        }