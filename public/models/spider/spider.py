from django.db import models
from public.models.spider.component import SpiderComponent


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
        app_label = 'public'
        managed = True
        db_table = 'public_spider'
        verbose_name = '已有爬虫'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.name
