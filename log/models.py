from django.db import models

# Create your models here.
class SpiderRunLog(models.Model):
    spider_name = models.CharField(max_length=255, verbose_name="爬虫名称")
    status = models.BooleanField(default=False, verbose_name="运行状态")
    unique_id = models.CharField(max_length=100, verbose_name="标识id", blank=True)
    task_id = models.CharField(max_length=100, verbose_name="任务id", blank=True)
    start_time = models.DateTimeField(auto_now=True, verbose_name="运行开始时间")
    end_time = models.DateTimeField(blank=True, null=True, verbose_name="运行结束时间")

    class Meta:
        managed = True
        db_table = 'log_spider'
        verbose_name = 'spider运行日志'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return "[" + self.spider_name + "]" + self.unique_id