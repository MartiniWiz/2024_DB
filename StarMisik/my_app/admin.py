from django.contrib import admin
from .models import Region, Tabelog, Google, FinalScore, User, Favorites


# Register your models here.

admin.site.register(Region)
admin.site.register(Tabelog)
admin.site.register(Google)
admin.site.register(FinalScore)
admin.site.register(User)
admin.site.register(Favorites)