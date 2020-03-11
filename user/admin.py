from django.contrib import admin
from user.models import *
# Register your models here.


admin.site.register(User)
admin.site.register(Role)
admin.site.register(Permission)
admin.site.register(Group)
admin.site.register(Menu)
