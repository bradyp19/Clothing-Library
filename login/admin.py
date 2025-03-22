from django.contrib import admin
from .models import Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'is_complete')  # add any other fields you want
    search_fields = ('user__username', 'user__email')
    list_filter = ('role',)

admin.site.register(Profile, ProfileAdmin)
