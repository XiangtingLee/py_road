from django.db import models


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
        app_label = 'public'
        managed = True
        db_table = 'public_spider_components'
        verbose_name = '爬虫组件'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.name

