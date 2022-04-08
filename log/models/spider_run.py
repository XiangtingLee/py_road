from django.db import models


class SpiderRunLog(models.Model):
    spider_name = models.CharField(max_length=255, verbose_name="爬虫名称")
    param = models.CharField(max_length=255, verbose_name="运行参数")
    task_id = models.CharField(max_length=255, verbose_name="任务id", blank=True)
    status = models.BooleanField(default=False, verbose_name="运行状态")
    start_time = models.DateTimeField(auto_now=True, verbose_name="运行开始时间")
    end_time = models.DateTimeField(blank=True, null=True, verbose_name="运行结束时间")
    remark = models.TextField(verbose_name="备注")

    class Meta:
        app_label = 'log'
        managed = True
        db_table = 'log_spider'
        verbose_name = 'spider运行日志'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return "[" + self.spider_name + "]" + self.task_id
