from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.views import View, generic
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q, Avg
from django.views.generic.list import ListView
from django.utils import timezone

from .forms import ItemForm, AddImageFormset, CollectionForm, CollectionFormPrivacy, BorrowRequestForm, ItemReviewForm, \
    get_wanted_items_queryset, AccessRequestForm, ClothingForm, ShoesForm
from .filters import ItemFilter, CollectionFilter
from closet.models import Item, Clothing, Shoes, Images, Collection, BorrowRequest, AccessRequest
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
        post_data = self.request.POST if self.request.POST else None
        context['addimageformset'] = AddImageFormset(post_data, self.request.FILES) if post_data else AddImageFormset()

        item_type = self.request.POST.get('item_type') if post_data else "CLOTHING"
        if item_type == "CLOTHING":
            context['subform'] = ClothingForm(post_data)
        elif item_type == "SHOES":
            context['subform'] = ShoesForm(post_data)
        else:
            context['subform'] = None
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        addimageformset = context['addimageformset']
        subform = context['subform']
        item_type = form.cleaned_data["item_type"]

        if not addimageformset.is_valid() or (subform and not subform.is_valid()):
            return self.form_invalid(form)

        item=form.save()

        if item_type == "CLOTHING":
            clothing = subform.save(commit=False)
            clothing.item_ptr = item
            clothing.save_base(raw=True)
        elif item_type == "SHOES":
            shoes = subform.save(commit=False)
            shoes.item_ptr = item
            shoes.save_base(raw=True)
        images = addimageformset.save(commit=False)
        for index, image in enumerate(images):
            image.item = item
            image.order = index
            image.save()
        return redirect(reverse("closet:closet_index")) # change this to redirect to desired page
def item_list(request):
    search = request.GET.get("q", None)

    if not request.user.is_authenticated:
        qs = get_wanted_items_queryset('public')
    elif is_librarian(request):
        qs = Item.objects.all()
    else:
        qs = get_wanted_items_queryset('public')

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
# def item_detail(request, item_id):
#     item = get_object_or_404(Item, pk=item_id)
#
#     item = item.clothing if hasattr(item, 'clothing') else item
#     item = item.shoes if hasattr(item, 'shoes') else item
#
#     context = {
#         'item': item,
#         'is_anonymous': not request.user.is_authenticated,
#         'is_librarian': hasattr(request.user, 'profile') and request.user.profile.role == 'librarian' if request.user.is_authenticated else False,
#         'is_patron': hasattr(request.user, 'profile') and request.user.profile.role == 'patron' if request.user.is_authenticated else False,
#     }
#     return render(request, 'closet/item_detail.html', context)

@login_required
def collections_list(request):
    # changed so that both librarian and patron can see all collections, handles public/private elsewhere
    search = request.GET.get("q", None)
    if not request.user.is_authenticated:
        qs = Collection.objects.filter(privacy_setting='PUBLIC')
    else:
        qs = Collection.objects.all()

    if search:
        qs = qs.filter(
            Q(name__icontains=search)
        )

    f = CollectionFilter(request.GET, queryset=qs)
    is_filtered = any(field in request.GET for field in f.get_fields())

    context = {
        'filter': f,
        'search_query': search,
        'is_filtered': is_filtered,
        # add other fields?
    }
    return render(request, 'closet/collection_list.html', context)

def public_collection_list(request):
    search = request.GET.get("q", None)
    qs = Collection.objects.filter(privacy_setting='PUBLIC')
    if search:
        qs = qs.filter(
            Q(name__icontains=search)
        )

    f = CollectionFilter(request.GET, queryset=qs)
    is_filtered = any(field in request.GET for field in f.get_fields())

    context = {
        'filter': f,
        'search_query': search,
        'is_filtered': is_filtered,
        # add other fields?
    }
    return render(request, 'closet/public_collections.html', context)

@login_required
def my_collections_list(request):
    # button to go to this view visible to patrons only... atm
    collections = Collection.objects.filter(owner=request.user)
    return render(request, 'closet/my_collections.html', {'collections': collections})

def collection_detail(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)
    search = request.GET.get("q", None)
    qs = collection.items.all()
    if search:
        qs = qs.filter(
            Q(item_name__icontains=search) | Q(brand__icontains=search)
        )
    context = {
        'collection': collection,
        'search_query': search,
        'qs': qs,
    }
    # guest access
    if collection.privacy_setting.lower() == 'public':
        return render(request, 'closet/collection_detail.html', context)
    elif request.user.is_authenticated and (request.user == collection.owner or has_access(request, collection_id) or is_librarian(request)):
        return render(request, 'closet/collection_detail.html', context)
    else:
    # Only allow access if the user is the owner or is a librarian or if collection is public
        if not (request.user == collection.owner or has_access(request, collection_id) or is_librarian(request) or collection.privacy_setting.lower() == 'public'):
            return HttpResponseForbidden("You are not allowed to view this collection.")

@login_required
def add_collection(request):
    if request.method == 'POST':
        if is_librarian(request):
            form = CollectionFormPrivacy(request.POST)
            privacy = request.POST.get('privacy_setting')
            if privacy:
                form.fields['items'].queryset = get_wanted_items_queryset(privacy.lower())
                if 'final_submit' not in request.POST:
                    form.data = form.data.copy()
                    form.data.setlist('items', [])
        else:
            form = CollectionForm(request.POST)
            form.fields['items'].queryset = get_wanted_items_queryset('public')
        if 'final_submit' in request.POST and form.is_valid():
            collection = form.save(commit=False)
            collection.owner = request.user
            collection.save()
            form.save_m2m()
            return redirect('closet:collections_list')
            # additional todos - if select private in librarian collection form, items that are in_collection should not be an option to select. for public, items that are in_private should not be options
    else:
        if is_librarian(request):
            form = CollectionFormPrivacy()
            #first is public
            form.fields['items'].queryset = get_wanted_items_queryset('public')
        else:
            form = CollectionForm()
            form.fields['items'].queryset = get_wanted_items_queryset('public')
    return render(request, 'closet/add_collection.html', {'form': form})

@login_required
def edit_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    # Only allow edit if user is librarian
    if not is_librarian(request):
        return HttpResponseForbidden("You are not allowed to edit this item.")
    item_type = 'CLOTHING' if hasattr(item, 'clothing') else 'SHOES' if hasattr(item, 'shoes') else None
    clothing_item = getattr(item, 'clothing', None)
    shoes_item = getattr(item, 'shoes', None)

    SubclassForm = ClothingForm if item_type == 'CLOTHING' else ShoesForm
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        addimageformset = AddImageFormset(request.POST, request.FILES, instance=item)

        subform = None
        if item_type == 'CLOTHING':
            subform = SubclassForm(request.POST, instance=clothing_item)
        elif item_type == 'SHOES':
            subform = SubclassForm(request.POST, instance=shoes_item)

        if form.is_valid() and addimageformset.is_valid() and (subform is None or subform.is_valid()):
           form.save()
           if subform:
               subform.save()
           addimageformset.save()
           return redirect('closet:item_detail', item_id=item.id)
    else:
        form = ItemForm(instance=item)
        addimageformset = AddImageFormset(instance=item)
        subform = None
        if item_type == 'CLOTHING':
            subform = SubclassForm(instance=clothing_item)
        elif item_type == 'SHOES':
            subform = SubclassForm(instance=shoes_item)
    context = {
        'form': form,
        'addimageformset': addimageformset,
        'subform': subform,
        'item': item,
        'item_type': item_type
    }
    return render(request, 'closet/edit_item.html', context)

#TODO: if item is the last item in a collection, and it is deleted, collection should also be deleted? requires some advanced logic with db query
@login_required
def delete_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    # Only allow delete if user is librarian
    if not is_librarian(request):
        return HttpResponseForbidden("You are not allowed to delete this item.")
    if request.method == 'POST':
        item.delete()
        return redirect('closet:closet_index')
    return render(request, 'closet/delete_item.html', {'item': item})

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
            return redirect('closet:collection_detail', collection_id=collection.id)
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

@login_required
def request_borrow_item(request, item_id):
    """
    Allows a patron to submit a borrow request from the item detail page.
    """
    item = get_object_or_404(Item, pk=item_id)
    # Optionally check if an existing pending request exists:
    existing = BorrowRequest.objects.filter(item=item, requester=request.user, status='PENDING').first()
    if existing:
        messages.info(request, "You already have a pending borrow request for this item.")
        return redirect('closet:item_detail', item_id=item.id)
    
    if request.method == "POST":
        form = BorrowRequestForm(request.POST)
        if form.is_valid():
            borrow_req = form.save(commit=False)
            borrow_req.item = item
            borrow_req.requester = request.user
            borrow_req.save()
            days = form.cleaned_data['borrow_duration']
            borrow_req.borrow_duration = days
            borrow_req.end_date = timezone.now().date() + timezone.timedelta(days=days)
            borrow_req.save()
            messages.success(request, "Your borrow request has been submitted.")
            return redirect('closet:item_detail', item_id=item.id)
    else:
        form = BorrowRequestForm()
    return render(request, 'closet/request_borrow.html', {'form': form, 'item': item})

@login_required
def my_borrow_requests(request):
    """
    Displays a list of borrow requests the current user has submitted.
    """
    borrow_requests = BorrowRequest.objects.filter(requester=request.user).exclude(status="RETURNED").order_by("-request_date")
    borrow_history = BorrowRequest.objects.exclude(status="PENDING").order_by("-updated_at")
    if request.method == "POST":
        request_id = request.POST.get('borrow_request_id')
        new_end_date = request.POST.get('new_end_date')
        borrow_request = get_object_or_404(BorrowRequest, id=request_id, requester=request.user)
        if borrow_request.status == 'APPROVED' and not borrow_request.extension_requested:
            borrow_request.extension_requested = True
            borrow_request.extended_date = new_end_date
            borrow_request.extension_status = 'PENDING'
            borrow_request.save()
            messages.success(request, "Extension request submitted.")
        else:
            messages.error(request, "You cannot request an extension for this borrow request.")

        return redirect('closet:my_borrow_requests')
    return render(request, 'closet/my_borrow_requests.html', {'borrow_requests': borrow_requests, 'borrow_history': borrow_history})

@login_required
def return_borrowed_item(request, request_id):
    borrow_request = get_object_or_404(BorrowRequest, id=request_id, requester=request.user)

    if borrow_request.item.status == 'OUT':
        borrow_request.status = 'RETURNED'
        borrow_request.item.status = 'IN'
        borrow_request.item.save()
        borrow_request.save()

        messages.success(request, "Item successfully returned. Thank you!")
    else:
        messages.error(request, "You cannot return this item.")

    return redirect('closet:my_borrow_requests')

@login_required
def review_borrow_requests(request):
    # Allow only librarians to access this view.
    if not (hasattr(request.user, 'profile') and request.user.profile.role.lower() == 'librarian'):
        return HttpResponseForbidden("You are not allowed to review borrow requests.")

    pending_requests = BorrowRequest.objects.filter(status="PENDING").order_by("request_date")
    pending_extensions = BorrowRequest.objects.filter(extension_requested=True, extension_status="PENDING").order_by("request_date")
    history_requests = BorrowRequest.objects.exclude(status="PENDING").order_by("-updated_at")

    return render(request, 'closet/review_borrow_requests.html', {
        'pending_requests': pending_requests,
        'pending_extensions': pending_extensions,
        'history_requests': history_requests,
    })

@login_required
def update_borrow_request(request, request_id, action):
    """
    Allows a librarian to approve or deny a borrow request.
    The parameter 'action' should be either 'approve' or 'deny'.
    """
    borrow_request = get_object_or_404(BorrowRequest, pk=request_id)
    if not (hasattr(request.user, 'profile') and request.user.profile.role.lower() == 'librarian'):
        return HttpResponseForbidden("You are not allowed to update borrow requests.")
    
    if action == "approve":
        if borrow_request.extension_requested and borrow_request.extension_status == "PENDING":
            borrow_request.end_date = borrow_request.extended_date
            borrow_request.extension_status = 'APPROVED'
        else:
            borrow_request.status = "APPROVED"
            borrow_request.item.status = "OUT"
            borrow_request.item.save()
            borrow_request.extension_status = 'APPROVED'
            borrow_request.end_date = borrow_request.extended_date or (
                timezone.now().date() + timezone.timedelta(days=borrow_request.borrow_duration)
            )
        
    elif action == "deny":
        if borrow_request.extension_requested and borrow_request.extension_status == "PENDING":
            borrow_request.extension_status = 'DENIED'
        else:
            borrow_request.status = "DENIED"
            borrow_request.extension_status = 'DENIED'
    else:
        messages.error(request, "Invalid action.")
        return redirect("closet:review_borrow_requests")
    
    borrow_request.save()
    messages.success(request, f"Borrow request has been {borrow_request.status.lower()}.")
    return redirect("closet:review_borrow_requests")

# @login_required
# def update_extension_request(request, request_id, action):
#     borrow_request = get_object_or_404(BorrowRequest, pk=request_id)
#     if not is_librarian(request):
#         return HttpResponseForbidden()

#     if action == 'approve':
#         borrow_request.end_date = borrow_request.extended_date
#         borrow_request.extension_status = 'APPROVED'
#     elif action == 'deny':
#         borrow_request.extension_status = 'DENIED'
#     borrow_request.save()
#     return redirect('closet:review_borrow_requests')

def item_detail(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    # Ensure we use the appropriate subclass if it exists
    if hasattr(item, 'clothing'):
        item = item.clothing
    elif hasattr(item, 'shoes'):
        item = item.shoes

    # Handle review submission
    if request.method == "POST" and 'rating' in request.POST:
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to submit a review.")
            return redirect("login:login")
        review_form = ItemReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.item = item
            review.reviewer = request.user
            review.save()
            messages.success(request, "Your review has been submitted.")
            return redirect('closet:item_detail', item_id=item.id)
        else:
            messages.error(request, "There was an error with your review. Please try again.")
    else:
        review_form = ItemReviewForm()

    # Retrieve existing reviews and compute the average rating
    reviews = item.reviews.all().order_by('-created_at')
    average_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']

    context = {
        'item': item,
        'review_form': review_form,
        'reviews': reviews,
        'average_rating': average_rating,
        'is_anonymous': not request.user.is_authenticated,
        'is_librarian': hasattr(request.user, 'profile') and request.user.profile.role == 'librarian' if request.user.is_authenticated else False,
        'is_patron': hasattr(request.user, 'profile') and request.user.profile.role == 'patron' if request.user.is_authenticated else False,
    }
    return render(request, 'closet/item_detail.html', context)

@login_required
def request_access_collection(request, collection_id):
    """
    Allows patrons to request access to private collections.
    Once they have access (theyre on access list), should be able to click on collection.
    """
    collection = get_object_or_404(Collection, id=collection_id)
    existing = AccessRequest.objects.filter(collection=collection, requester=request.user, status='PENDING').first()
    if existing or collection.access_list.filter(pk=request.user.pk).exists():
        messages.error(request, "You have already requested access to this collection.")
        return redirect('closet:collections_list')

    if request.method == "POST":
        form = AccessRequestForm(request.POST)
        if form.is_valid():
            access_req = form.save(commit=False)
            access_req.collection = collection
            access_req.requester = request.user
            access_req.save()
            messages.success(request, "Your access request has been submitted.")
            return redirect('closet:collections_list')
    else:
        form = AccessRequestForm()
    return render(request, 'closet/access_request.html', {'form': form, 'collection': collection})

@login_required
def review_access_requests(request):
    # Only for librarians
    if not (hasattr(request.user, 'profile') and is_librarian(request)):
        return HttpResponseForbidden("You are not allowed to review borrow requests.")

    pending_requests = AccessRequest.objects.filter(status='PENDING').order_by('request_date')

    return render(request, 'closet/review_access_requests.html', {'pending_requests': pending_requests})

@login_required
def update_access_request(request, request_id, action):
    """
    Allows a librarian to approve or deny access request, at which point user will be added to access list.
    """
    access_request = get_object_or_404(AccessRequest, pk=request_id)
    if not (hasattr(request.user, 'profile') and is_librarian(request)):
        return HttpResponseForbidden("You are not allowed to update borrow requests.")

    if action == "approve":
        access_request.status = "APPROVED"
        collection = access_request.collection
        collection.access_list.add(access_request.requester)
    elif action == "deny":
        access_request.status = "DENIED"
    else:
        messages.error(request, "Invalid action.")
        return redirect('closet:review_access_requests')

    access_request.save()
    messages.success(request, f"Access request has been {access_request.status.lower()}.")
    return redirect('closet:review_access_requests')

def has_access(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)
    return collection.access_list.filter(pk=request.user.pk).exists()
