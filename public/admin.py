from django.contrib import admin

from public.models.district.administration import AdministrativeDiv
from public.models.spider.spider import Spider

# Register your models here.
admin.site.register(AdministrativeDiv)
admin.site.register(Spider)
