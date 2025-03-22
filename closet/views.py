from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.views import View, generic
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.generic.list import ListView

from .forms import ItemForm, AddImageFormset 
from .filters import ItemFilter
from closet.models import Item, Clothing, Shoes, Images

class AddView(generic.CreateView):
    model = Item
    form_class = ItemForm
    template_name = "closet/add.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['addimageformset'] = AddImageFormset(self.request.POST, self.request.FILES)
        else:
            context['addimageformset'] = AddImageFormset()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        addimageformset = context['addimageformset']
        
        if form.is_valid() and addimageformset.is_valid():
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
     
            images = addimageformset.save(commit=False)
            for index, image in enumerate(images):
                image.item = item
                image.order = index
                image.save()
            return redirect(reverse("closet:closet_index")) # change this to redirect to desired page
        else:
            return self.render_to_response(self.get_context_data(form=form, addimageformset=addimageformset))

class IndexView(generic.ListView):
    template_name = "closet/closet_index.html"
    context_object_name = "items_in_closet"

    def get_queryset(self):
            return Item.objects.all()

def item_list(request):
    f = ItemFilter(request.GET, queryset=Item.objects.all())
    return render(request, 'closet/closet_index.html', {'filter': f})

#using this instead of using generic DetailView, so in urls.py pk changed to item_id
def item_detail(request, item_id):
    item = get_object_or_404(Item, pk=item_id)

    item = item.clothing if hasattr(item, 'clothing') else item
    item = item.shoes if hasattr(item, 'shoes') else item

    return render(request, 'closet/item_detail.html', {'item': item})
