from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from models import UserProfile

admin.site.unregister(User)
 
class UserProfileInline(admin.StackedInline):
    max_num = 1
    model = UserProfile
 
class UserProfileAdmin(UserAdmin):
    inlines = [UserProfileInline]

admin.site.register(User, UserProfileAdmin)
