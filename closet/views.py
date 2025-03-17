from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect
from django.views import View, generic
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.generic.list import ListView

from .forms import ItemForm
from closet.models import Item, Clothing, Shoes, Images

class AddView(generic.CreateView):
    model = Item
    form_class = ItemForm
    template_name = "closet/add.html"

    def form_valid(self, form):
        item = form.save(commit=False)
        item.save()

        item_type = form.cleaned_data["item_type"]
        if item_type == "CLOTHING":
            clothing = Clothing(
                item_ptr=item, #multi-table inheritance 1 to 1 relationship
                size=form.cleaned_data["clothing_size"]
            )
            clothing.save_base(raw=True) #dont save parent Item instance again
        elif item_type == "SHOES":
            shoes = Shoes(
                item_ptr=item,
                size=form.cleaned_data["shoes_size"]
            )
            shoes.save_base(raw=True)
        
        if self.request.FILES.getlist("images"):
            images = self.request.FILES.getlist("images")
            for index, image in enumerate(images):
                Images.objects.create(item=item, image=image, order=index)
        return redirect(reverse("closet:dashboard")) # change this to redirect to desired page
