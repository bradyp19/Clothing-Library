from django import forms

from .models import Item, Clothing, Shoes

class ItemForm(forms.ModelForm):
    ITEM_TYPE_CHOICES = [
        ("CLOTHING", "Clothing"),
        ("SHOES", "Shoes"),
    ]
    item_type = forms.ChoiceField(choices=ITEM_TYPE_CHOICES, widget=forms.Select(attrs={"id": "item-type"}))

    class Meta:
        model = Item
        fields = ["item_name", "brand", "condition", "fit", "occasion", "gender"]

    clothing_size = forms.ChoiceField(choices=Clothing.SIZE_CHOICES, required=False, widget=forms.Select(attrs={"id": "clothing-size"}))
    shoes_size = forms.ChoiceField(choices=Shoes.SIZE_CHOICES, required=False, widget=forms.Select(attrs={"id": "shoes-size"}))

