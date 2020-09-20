from django.db import models
from public.models import AdministrativeDiv

# Create your models here.


class DXYData(models.Model):
    statistics = models.TextField(verbose_name='顶部数据', blank=True)
    rumor = models.TextField(verbose_name='辟谣数据', blank=True)
    timeline = models.TextField(verbose_name='时间线新闻数据', blank=True)
    domestic_province = models.TextField(verbose_name='国内省级数据', blank=True)
    domestic_area = models.TextField(verbose_name='国内地区数据', blank=True)
    foreign = models.TextField(verbose_name='国外数据', blank=True)
    add_time = models.DateTimeField(verbose_name="添加时间", auto_now=True)
    modify_time = models.DateTimeField(verbose_name="修改时间")
    is_available = models.BooleanField(default=True, verbose_name='是否可用')
    is_delete = models.BooleanField(default=False, verbose_name='是否删除')
    remark = models.TextField(verbose_name="备注")

    class Meta:
        managed = True
        db_table = 'COVID19_DXY_Data'
        verbose_name = '丁香园数据'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.modify_time.strftime("%Y-%m-%d %H:%M:%S")


class DXYTimeLine(models.Model):
    id = models.IntegerField(verbose_name="id", primary_key=True)
    title = models.CharField(null=True, blank=True, max_length=255, verbose_name="标题")
    source_url = models.URLField(null=True, blank=True, max_length=255, verbose_name="来源链接")
    source_info = models.CharField(null=True, blank=True, max_length=255, verbose_name="来源名称")
    source_summary = models.TextField(null=True, blank=True, verbose_name="来源详情")
    province = models.ForeignKey(AdministrativeDiv, on_delete=models.CASCADE, null=True, blank=True, verbose_name="省份")
    info_type = models.IntegerField(null=True, blank=True, verbose_name="消息类型")
    publish_time = models.DateTimeField(verbose_name="发布时间")
    create_time = models.DateTimeField(verbose_name="采集时间")
    modify_time = models.DateTimeField(verbose_name="最后修改时间")
    is_available = models.BooleanField(default=True, verbose_name='是否可用')
    is_delete = models.BooleanField(default=False, verbose_name='是否删除')

    class Meta:
        managed = True
        db_table = 'COVID19_DXY_timeline'
        verbose_name = '丁香园发展时间线'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.title
