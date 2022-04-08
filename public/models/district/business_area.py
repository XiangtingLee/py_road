from django.db import models
from public.models.district.administration import AdministrativeDiv


class CityBusinessArea(models.Model):
    name = models.CharField(max_length=100, verbose_name='商圈名称', blank=True)
    district = models.ForeignKey(AdministrativeDiv, on_delete=models.CASCADE, null=True, blank=True)
    add_time = models.DateTimeField(verbose_name="添加时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_effective = models.BooleanField(default=True, verbose_name="是否有效")
    area = ''

    class Meta:
        app_label = 'public'
        managed = True
        db_table = 'public_city_business_area'
        verbose_name = '全国城市商圈'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.name
