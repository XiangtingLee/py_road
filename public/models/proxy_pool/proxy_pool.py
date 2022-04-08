from django.db import models
from public.models.proxy_pool.type import ProxyPoolType
from public.models.proxy_pool.method import ProxyMethod
from public.models.proxy_pool.protocol import ProxyPoolProtocol


class ProxyPool(models.Model):
    protocol = models.ForeignKey(ProxyPoolProtocol, on_delete=models.CASCADE, verbose_name='代理协议')
    address = models.CharField(max_length=15, verbose_name='代理地址')
    port = models.CharField(max_length=10, verbose_name='代理端口号')
    type = models.ForeignKey(ProxyPoolType, on_delete=models.CASCADE, verbose_name='代理类型')
    method = models.ForeignKey(ProxyMethod, on_delete=models.CASCADE, verbose_name='请求方式', null=True, blank=True)
    add_time = models.DateTimeField(verbose_name="添加时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_available = models.BooleanField(default=False, verbose_name='是否可用')
    is_delete = models.BooleanField(default=False, verbose_name='是否删除')

    class Meta:
        app_label = 'public'
        managed = True
        db_table = 'public_proxy_pool'
        verbose_name = '代理池'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.protocol.name + "://" + self.address + ':' + str(self.port)
