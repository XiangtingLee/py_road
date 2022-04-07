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
        managed = True
        db_table = 'public_administrative_div'
        verbose_name = '全国行政区划'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.name


class CityBusinessArea(models.Model):
    name = models.CharField(max_length=100, verbose_name='商圈名称', blank=True)
    district = models.ForeignKey(AdministrativeDiv, on_delete=models.CASCADE, null=True, blank=True)
    add_time = models.DateTimeField(verbose_name="添加时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_effective = models.BooleanField(default=True, verbose_name="是否有效")
    area = ''

    class Meta:
        managed = True
        db_table = 'public_city_business_area'
        verbose_name = '全国城市商圈'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.name


class ProxyPoolType(models.Model):
    name = models.CharField(max_length=128, verbose_name="名称")
    add_time = models.DateTimeField(verbose_name="添加时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_available = models.BooleanField(default=True, verbose_name='是否可用')
    is_delete = models.BooleanField(default=False, verbose_name='是否删除')

    class Meta:
        managed = True
        db_table = 'public_proxy_pool_type'
        verbose_name = '代理类型'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.name


class ProxyPoolProtocol(models.Model):
    name = models.CharField(max_length=16, verbose_name="名称")
    add_time = models.DateTimeField(verbose_name="添加时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_available = models.BooleanField(default=True, verbose_name='是否可用')
    is_delete = models.BooleanField(default=False, verbose_name='是否删除')

    class Meta:
        managed = True
        db_table = 'public_proxy_pool_protocol'
        verbose_name = '代理协议'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.name

class ProxyMethodType(models.Model):
    name = models.CharField(max_length=16, verbose_name="名称")
    add_time = models.DateTimeField(verbose_name="添加时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_available = models.BooleanField(default=True, verbose_name='是否可用')
    is_delete = models.BooleanField(default=False, verbose_name='是否删除')

    class Meta:
        managed = True
        db_table = 'public_proxy_pool_method'
        verbose_name = '代理请求方式'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.name


class ProxyPool(models.Model):
    protocol = models.ForeignKey(ProxyPoolProtocol, on_delete=models.CASCADE, verbose_name='代理协议')
    address = models.CharField(max_length=15, verbose_name='代理地址')
    port = models.CharField(max_length=10, verbose_name='代理端口号')
    type = models.ForeignKey(ProxyPoolType, on_delete=models.CASCADE, verbose_name='代理类型')
    method = models.ForeignKey(ProxyMethodType, on_delete=models.CASCADE, verbose_name='请求方式', null=True, blank=True)
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
        return self.protocol.name + "://" + self.address + ':' + str(self.port)


class SpiderComponent(models.Model):
    name = models.CharField(max_length=100, verbose_name="模块名称", null=True, blank=True)
    code = models.TextField(default={}, verbose_name="模块代码")
    data = models.JSONField(verbose_name="附加数据", null=True, blank=True)
    description = models.TextField(verbose_name="描述", null=True, blank=True)
    add_time = models.DateTimeField(verbose_name="添加时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    frame_available = models.BooleanField(default=True, verbose_name='框架爬虫是否可用')
    is_available = models.BooleanField(default=False, verbose_name='是否可用')
    is_delete = models.BooleanField(default=False, verbose_name='是否删除')

    class Meta:
        managed = True
        db_table = 'public_spider_components'
        verbose_name = '爬虫组件'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.name


class Spider(models.Model):
    name = models.CharField(max_length=100, verbose_name='爬虫名称', blank=True)
    path = models.CharField(max_length=255, verbose_name='爬虫路径')
    component = models.ManyToManyField(SpiderComponent, blank=True, verbose_name="操作组件")
    add_time = models.DateTimeField(verbose_name="添加时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_frame = models.BooleanField(default=False, verbose_name='是否为框架爬虫')
    is_available = models.BooleanField(default=False, verbose_name='是否可用')
    is_delete = models.BooleanField(default=False, verbose_name='是否删除')
    remark = models.TextField(verbose_name="备注")

    class Meta:
        managed = True
        db_table = 'public_spider'
        verbose_name = '已有爬虫'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.name
