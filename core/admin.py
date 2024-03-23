from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.contenttypes.admin import GenericTabularInline

from tags.models import TaggedItem
from .models import User

# Register your models here.
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    (None, {
        'classes': ('wide',),
        'fields':('username','password1','password2','email', 'first_name', 'last_name')
    }),
 
class TagInline(GenericTabularInline):
    autocomplete_fields = ['tag']
    model = TaggedItem