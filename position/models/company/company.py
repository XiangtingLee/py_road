from django.db import models

from position.models.company.size import CompanySize
from position.models.company.label import CompanyLabels
from position.models.company.businessInfo import CompanyBusinessInfo
from position.models.company.financing import CompanyFinancing
from position.models.company.industry import CompanyIndustries
from public.models.district.administration import AdministrativeDiv


class Company(models.Model):
    # core info
    id = models.IntegerField(primary_key=True, verbose_name='公司id', blank=True, default=None)
    name = models.CharField(blank=True, null=True, max_length=100, verbose_name="公司名称")
    city = models.ForeignKey(AdministrativeDiv, on_delete=models.CASCADE, blank=True, null=True, verbose_name="所在地区")
    short_name = models.CharField(blank=True, null=True, max_length=50, verbose_name="公司简称")
    introduction = models.CharField(blank=True, null=True, max_length=255, verbose_name="公司简介")
    profile = models.TextField(blank=True, null=True, verbose_name="公司介绍")
    certification = models.BooleanField(blank=True, default=True, verbose_name="公司认证")
    financing = models.ForeignKey(CompanyFinancing, on_delete=models.CASCADE, blank=True, null=True,
                                  verbose_name="融资阶段")
    size = models.ForeignKey(CompanySize, on_delete=models.CASCADE, blank=True, null=True, verbose_name="公司规模")
    industry = models.ManyToManyField(CompanyIndustries, blank=True, verbose_name="公司所属行业")
    url = models.URLField(blank=True, null=True, max_length=255, verbose_name="公司官网")
    logo = models.CharField(blank=True, null=True, max_length=255, verbose_name="公司logo")
    label = models.ManyToManyField(CompanyLabels, blank=True, verbose_name="公司标签")
    business_info = models.ForeignKey(CompanyBusinessInfo, on_delete=models.CASCADE, blank=True, null=True,
                                      verbose_name="工商信息")
    is_effective = models.BooleanField(blank=True, default=True, verbose_name="是否有效")
    add_time = models.DateTimeField(blank=True, null=True, verbose_name="新增时间")
    update_time = models.DateTimeField(blank=True, null=True, auto_now=True, verbose_name="更新时间")

    class Meta:
        app_label = 'position'
        managed = True
        db_table = 'position_company'
        verbose_name = '招聘公司'
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.id) if not self.name else self.name
