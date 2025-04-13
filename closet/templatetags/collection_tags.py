from django import template

register = template.Library()

@register.filter(name='has_access')
def has_access(collection, user):
    return collection.access_list.filter(pk=user.pk).exists()