from django.contrib import admin
from movies.models import *
# Register your models here.
admin.site.register(Genre)
admin.site.register(Platform)
admin.site.register(Language)
admin.site.register(Person)
admin.site.register(Review)
admin.site.register(Movie)
admin.site.register(WebShow)
admin.site.register(WebSeason)
admin.site.register(Episode)
admin.site.register(PersonRole)

