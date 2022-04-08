from django.db import models


class PositionNature(models.Model):
    name = models.CharField(max_length=20, verbose_name="类型名称")
    add_time = models.DateTimeField(verbose_name="新增时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_effective = models.BooleanField(default=True, verbose_name="是否有效")

    class Meta:
        app_label = 'position'
        managed = True
        db_table = 'position_position_nature'
        verbose_name = '职位性质'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
