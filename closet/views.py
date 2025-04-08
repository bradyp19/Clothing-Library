from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.views import View, generic
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Q
from django.views.generic.list import ListView

from .forms import ItemForm, AddImageFormset, CollectionForm, CollectionFormPrivacy, get_wanted_items_queryset
from .filters import ItemFilter
from closet.models import Item, Clothing, Shoes, Images, Collection
from login.models import Librarian, Patron, Profile

class AddView(generic.CreateView):
    model = Item
    form_class = ItemForm
    template_name = "closet/add.html"

    def dispatch(self, request, *args, **kwargs):
        if not (hasattr(request.user, 'profile') and request.user.profile.role == 'librarian'):
            return HttpResponseForbidden("Only librarians can add items.")
        return super().dispatch(request, *args, **kwargs)

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
def item_list(request):
    search = request.GET.get("q", None)
    qs = Item.objects.all()
    if search:
        qs = qs.filter(
            Q(item_name__icontains=search) | Q(brand__icontains=search)
        )

    f = ItemFilter(request.GET, queryset=qs)
    is_filtered = any(field in request.GET for field in f.get_fields())

    context = {
        'filter': f,
        'search_query': search,
        'is_filtered': is_filtered,
        'is_anonymous': not request.user.is_authenticated,
        'is_librarian': hasattr(request.user, 'profile') and request.user.profile.role == 'librarian' if request.user.is_authenticated else False,
        'is_patron': hasattr(request.user, 'profile') and request.user.profile.role == 'patron' if request.user.is_authenticated else False,
    }
    return render(request, 'closet/closet_index.html', context)

#using this instead of using generic DetailView, so in urls.py pk changed to item_id
def item_detail(request, item_id):
    item = get_object_or_404(Item, pk=item_id)

    item = item.clothing if hasattr(item, 'clothing') else item
    item = item.shoes if hasattr(item, 'shoes') else item

    context = {
        'item': item,
        'is_anonymous': not request.user.is_authenticated,
        'is_librarian': hasattr(request.user, 'profile') and request.user.profile.role == 'librarian' if request.user.is_authenticated else False,
        'is_patron': hasattr(request.user, 'profile') and request.user.profile.role == 'patron' if request.user.is_authenticated else False,
    }
    return render(request, 'closet/item_detail.html', context)

@login_required
def collections_list(request):
    # changed so that both librarian and patron can see all collections, handles public/private elsewhere
    collections = Collection.objects.all()
    return render(request, 'closet/collection_list.html', {'collections': collections})

@login_required
def my_collections_list(request):
    # button to go to this view visible to patrons only... atm
    collections = Collection.objects.filter(owner=request.user)
    return render(request, 'closet/my_collections.html', {'collections': collections})
@login_required
def collection_detail(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)
    # Only allow access if the user is the owner or is a librarian or if collection is public
    if not (request.user == collection.owner or is_librarian(request) or collection.privacy_setting.lower() == 'public'):
        return HttpResponseForbidden("You are not allowed to view this collection.")
    return render(request, 'closet/collection_detail.html', {'collection': collection})

@login_required
def add_collection(request):
    if request.method == 'POST':
        if is_librarian(request):
            form = CollectionFormPrivacy(request.POST)
        else:
            form = CollectionForm(request.POST)
            form.fields['items'].queryset = get_wanted_items_queryset('public')
        if form.is_valid():
            collection = form.save(commit=False)
            collection.owner = request.user
            # # Force collections created by non-librarians (Patrons) to be public
            # if not (hasattr(request.user, 'profile') and request.user.profile.role == 'librarian'):
            #     collection.privacy_setting = 'PUBLIC'
            collection.save()
            form.save_m2m()
            # # Optionally, populate access_list here (e.g., add owner and all librarians)
            # collection.access_list.add(request.user)
            # from django.contrib.auth import get_user_model
            # User = get_user_model()
            # librarians = User.objects.filter(profile__role='librarian')
            # for librarian in librarians:
            #     collection.access_list.add(librarian)
            return redirect('closet:collections_list')
            # additional todos - if select private in librarian collection form, items that are in_collection should not be an option to select. for public, items that are in_private should not be options
    else:
        if is_librarian(request):
            form = CollectionFormPrivacy()
        else:
            form = CollectionForm()
            form.fields['items'].queryset = get_wanted_items_queryset('public')
    return render(request, 'closet/add_collection.html', {'form': form})

@login_required
def edit_collection(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)
    # Only allow edit if the user is the owner or a librarian.
    if not (request.user == collection.owner or is_librarian(request)):
        return HttpResponseForbidden("You are not allowed to edit this collection.")
    if request.method == 'POST':
        form = CollectionForm(request.POST, instance=collection)
        if collection.privacy_setting.lower() == 'public': #if public collection
            form.fields['items'].queryset = get_wanted_items_queryset('public')
        else: #else if private, want to load items not in collection OR in current collection
            q1 = get_wanted_items_queryset('private')
            q2 = collection.items.all()
            form.fields['items'].queryset = q1 | q2
        if form.is_valid():
            form.save()
            return redirect('closet:collections_list')
    else:
        form = CollectionForm(instance=collection) # editing privacy setting after creation not smth we have, decide if that's what we want because it might complicate things
        if collection.privacy_setting.lower() == 'public': #if public collection
            form.fields['items'].queryset = get_wanted_items_queryset('public')
        else: #else if private, want to load items not in collection OR in current collection
            q1 = get_wanted_items_queryset('private')
            q2 = collection.items.all()
            form.fields['items'].queryset = q1 | q2
    return render(request, 'closet/edit_collection.html', {'form': form, 'collection': collection})

@login_required
def delete_collection(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)
    # Only allow delete if the user is the owner or a librarian.
    if not (request.user == collection.owner or is_librarian(request)):
        return HttpResponseForbidden("You are not allowed to delete this collection.")
    if request.method == 'POST':
        collection.delete()
        return redirect('closet:collections_list')
    return render(request, 'closet/delete_collection.html', {'collection': collection})

def is_librarian(request):
    profile = request.user.profile
    if profile.role.lower() == 'librarian':
        return True

#def in_collection_access_list(request, collection):
