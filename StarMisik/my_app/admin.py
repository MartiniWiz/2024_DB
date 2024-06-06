from django.contrib import admin
from .models import Region, Tabelog, Google, FinalScore, User, Favorites
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .models import User

# Register your models here.
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'age', 'sex', 'is_admin', 'is_staff')
    search_fields = ('username',)
    readonly_fields = ('id',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('age', 'sex')}),
        ('Permissions', {'fields': ('is_admin', 'is_staff')}),
    )

admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
admin.site.register(Region)
admin.site.register(Tabelog)
admin.site.register(Google)
admin.site.register(FinalScore)
admin.site.register(Favorites)