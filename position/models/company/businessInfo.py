from django.db import models
from .regStatus import CompanyRegStatus


class CompanyBusinessInfo(models.Model):
    cid = models.IntegerField(primary_key=True, verbose_name='公司id', blank=True, default=None)
    tyc_id = models.CharField(blank=True, null=True, max_length=20, verbose_name="天眼查id")
    full_name = models.CharField(blank=True, null=True, max_length=255, verbose_name="工商-公司名称")
    credit_code = models.CharField(null=True, blank=True, max_length=20, verbose_name="工商-公司信用代码")
    establish_time = models.DateField(null=True, blank=True, verbose_name="工商-成立时间")
    reg_capital = models.CharField(blank=True, null=True, max_length=20, verbose_name="工商-注册资本")
    reg_location = models.CharField(blank=True, null=True, max_length=255, verbose_name="工商-注册地点")
    legal_person_name = models.CharField(blank=True, null=True, max_length=255, verbose_name="工商-法人姓名")
    reg_status = models.ForeignKey(CompanyRegStatus, on_delete=models.CASCADE, blank=True, null=True,
                                   verbose_name="工商-经营状态")
    add_time = models.DateTimeField(verbose_name="新增时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_effective = models.BooleanField(default=True, verbose_name="是否有效")

    class Meta:
        app_label = 'position'
        managed = True
        db_table = 'position_company_business'
        verbose_name = '公司工商信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.id) if not self.full_name else self.full_name
