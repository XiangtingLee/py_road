from django.db import models


class ProxyPoolProtocol(models.Model):
    name = models.CharField(max_length=16, verbose_name="名称")
    add_time = models.DateTimeField(verbose_name="添加时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_available = models.BooleanField(default=True, verbose_name='是否可用')
    is_delete = models.BooleanField(default=False, verbose_name='是否删除')

    class Meta:
        app_label = 'public'
        managed = True
        db_table = 'public_proxy_pool_protocol'
        verbose_name = '代理协议'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.name
