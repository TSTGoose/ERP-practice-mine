from django.template.defaulttags import register

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def index(indexable, i):
    return indexable[i]

@register.filter 
def get_set(Queryset):
    return Queryset.id