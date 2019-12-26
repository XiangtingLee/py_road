from django.db import models

# Create your models here.

class AdministrativeDiv(models.Model):
    code = models.IntegerField(verbose_name='地区编码')
    name = models.CharField(max_length=100, verbose_name='地区名称', blank=True)
    pinyin = models.CharField(null=True, blank=True, max_length=100, verbose_name='拼音名')
    short_name = models.CharField(null=True, blank=True, max_length=100, verbose_name='简称')
    zip_code = models.IntegerField(null=True, blank=True, verbose_name='邮政编码')
    province = models.ForeignKey('self', null=True, blank=True, verbose_name='省', on_delete=models.CASCADE, related_name="level1")
    city = models.ForeignKey('self', null=True, blank=True, verbose_name='市', on_delete=models.CASCADE, related_name="level2")
    area = models.ForeignKey('self', null=True, blank=True, verbose_name='区', on_delete=models.CASCADE, related_name="level3")
    lng_lat = models.CharField(null=True, blank=True, max_length=100, verbose_name='经纬度')
    add_time = models.DateTimeField(verbose_name="添加时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_effective = models.BooleanField(default=True, verbose_name="是否有效")

    class Meta:
        managed = True
        db_table = 'public_administrative_div'
        verbose_name = '全国行政区划'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.name

class CityBusinessZone(models.Model):
    name = models.CharField(max_length=100, verbose_name='商圈名称', blank=True)
    province = models.ForeignKey(AdministrativeDiv, on_delete=models.CASCADE, null=True, blank=True, related_name="business_level1")
    city = models.ForeignKey(AdministrativeDiv, on_delete=models.CASCADE, null=True, blank=True, related_name="business_level2")
    area = models.ForeignKey(AdministrativeDiv, on_delete=models.CASCADE, null=True, blank=True, related_name="business_level3")

    add_time = models.DateTimeField(verbose_name="添加时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_effective = models.BooleanField(default=True, verbose_name="是否有效")

    class Meta:
        managed = True
        db_table = 'public_city_business_zone'
        verbose_name = '全国城市商圈'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.name

class ProxyPool(models.Model):
    protocol = models.CharField(max_length=6, verbose_name='代理协议')
    address = models.CharField(max_length=15, verbose_name='代理地址')
    port = models.CharField(max_length=10, verbose_name='代理端口号')
    type = models.CharField(max_length=255, verbose_name='代理类型')
    add_time = models.DateTimeField(verbose_name="添加时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_available = models.BooleanField(default=False, verbose_name='是否可用')
    is_delete = models.BooleanField(default=False, verbose_name='是否删除')

    class Meta:
        managed = True
        db_table = 'public_proxy_pool'
        verbose_name = '代理池'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.address + ':' + str(self.port)
