from django.contrib import admin

from .models import Item, Clothing, Shoes, Images

class ImagesInline(admin.TabularInline):  
    """Allows adding images inline within the Item admin page."""
    model = Images
    extra = 1 


class ClothingAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'brand', 'get_condition_display', 'get_fit_display', 'get_occasion_display', 'get_gender_display', 'size', 'get_clothing_type_display')
    list_filter = ('brand', 'condition', 'fit', 'occasion', 'gender', 'clothing_type', 'size')
    search_fields = ('item_name', 'brand')
    inlines = [ImagesInline]

class ShoesAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'brand', 'get_condition_display', 'get_fit_display', 'get_occasion_display', 'get_gender_display', 'size')
    list_filter = ('brand', 'condition', 'fit', 'occasion', 'gender', 'size')
    search_fields = ('item_name', 'brand')
    inlines = [ImagesInline]

class ImagesAdmin(admin.ModelAdmin):
    list_display = ('item', 'image', 'order')
    list_filter = ('item',)
    ordering = ['order']

admin.site.register(Clothing, ClothingAdmin)
admin.site.register(Shoes, ShoesAdmin)
admin.site.register(Images, ImagesAdmin)