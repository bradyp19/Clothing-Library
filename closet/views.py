from django.shortcuts import render,redirect, get_object_or_404
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
                size=form.cleaned_data["clothing_size"],
                clothing_type=form.cleaned_data["clothing_type"]
            )
            clothing.save_base(raw=True) #dont save parent Item instance again
        elif item_type == "SHOES":
            shoes = Shoes(
                item_ptr=item,
                size=form.cleaned_data["shoes_size"]
            )
            shoes.save_base(raw=True)
        if self.request.method == 'POST':
            if "images" in self.request.FILES:
                images = self.request.FILES.getlist("images")
                for index, image in enumerate(images):
                    uploaded_image = image
                    uploaded_image.seek(0)  
                    Images.objects.create(item=item, image=uploaded_image, order=index)
        return redirect(reverse("closet:closet_index")) # change this to redirect to desired page
    
class IndexView(generic.ListView):
    template_name = "closet/closet_index.html"
    context_object_name = "items_in_closet"

    def get_queryset(self):
        """Return the last five published qucestions (not including those set to be published in the future)."""
        return Item.objects.all()

#using this instead of using generic DetailView, so in urls.py pk changed to item_id
def item_detail(request, item_id):
    item = get_object_or_404(Item, pk=item_id)

    item = item.clothing if hasattr(item, 'clothing') else item
    item = item.shoes if hasattr(item, 'shoes') else item

    return render(request, 'closet/item_detail.html', {'item': item})
