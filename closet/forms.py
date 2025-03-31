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
        fields = ['name', 'description',] #no option for privacy setting, so default will be saved
    items = CustomMMCF(
        queryset=Item.objects.all(),
        widget=forms.CheckboxSelectMultiple()
    )

class CollectionFormLibrarian(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['name', 'description', 'privacy_setting']
    items = CustomMMCF(
        queryset=Item.objects.all(),
        widget=forms.CheckboxSelectMultiple()
    )
AddImageFormset = forms.inlineformset_factory(Item, Images, extra=3, form=ImageForm, can_delete=False)