from django.db import models


class AdministrativeDiv(models.Model):
    code = models.CharField(max_length=10, null=True, blank=True, verbose_name='地区编码')
    name = models.CharField(max_length=100, verbose_name='地区名称', blank=True)
    pinyin = models.CharField(null=True, blank=True, max_length=100, verbose_name='拼音名')
    short_name = models.CharField(null=True, blank=True, max_length=100, verbose_name='简称')
    zip_code = models.IntegerField(null=True, blank=True, verbose_name='邮政编码')
    province = models.ForeignKey('self', null=True, blank=True, verbose_name='省', on_delete=models.CASCADE,
                                 related_name="level1")
    city = models.ForeignKey('self', null=True, blank=True, verbose_name='市', on_delete=models.CASCADE,
                             related_name="level2")
    area = models.ForeignKey('self', null=True, blank=True, verbose_name='区', on_delete=models.CASCADE,
                             related_name="level3")
    lng_lat = models.CharField(null=True, blank=True, max_length=100, verbose_name='经纬度')
    add_time = models.DateTimeField(verbose_name="添加时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_effective = models.BooleanField(default=True, verbose_name="是否有效")

    class Meta:
        app_label = 'public'
        managed = True
        db_table = 'public_administrative_div'
        verbose_name = '全国行政区划'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.name
