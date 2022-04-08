from django.db import models

from position.models.company.company import Company
from position.models.position.type import PositionType
from position.models.position.label import PositionLabels
from position.models.position.nature import PositionNature
from position.models.position.welfare import PositionWelfares
from position.models.position.education import PositionEducation
from position.models.position.experience import PositionExperience
from public.models.district.business_area import CityBusinessArea
from public.models.district.administration import AdministrativeDiv


class Position(models.Model):
    # 公司相关
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="公司id", null=True, blank=True)
    # 职位相关
    id = models.IntegerField(primary_key=True, verbose_name='职位id')
    name = models.CharField(blank=True, null=True, max_length=100, verbose_name="职位名称")
    description = models.TextField(blank=True, null=True, verbose_name="职位描述")
    type = models.ForeignKey(PositionType, on_delete=models.CASCADE, blank=True, null=True, verbose_name="职位类型")
    nature = models.ForeignKey(PositionNature, on_delete=models.CASCADE, blank=True, null=True, verbose_name="职位性质")
    city = models.ForeignKey(AdministrativeDiv, on_delete=models.CASCADE, blank=True, null=True,
                             verbose_name="所在城市", related_name="position_level1")
    district = models.ForeignKey(AdministrativeDiv, on_delete=models.CASCADE, blank=True, null=True,
                                 verbose_name="所在区域", related_name="position_level2")
    business_area = models.ForeignKey(CityBusinessArea, on_delete=models.CASCADE, blank=True, null=True,
                                      verbose_name="所在商圈")
    street = models.CharField(blank=True, null=True, max_length=255, verbose_name="详细地址")
    education = models.ForeignKey(PositionEducation, on_delete=models.CASCADE, blank=True, null=True,
                                  verbose_name="学历要求")
    experience = models.ForeignKey(PositionExperience, on_delete=models.CASCADE, blank=True, null=True,
                                   verbose_name="经验要求")
    salary_lower = models.IntegerField(verbose_name="薪水下限")
    salary_upper = models.IntegerField(verbose_name="薪水上限")
    welfare = models.ManyToManyField(PositionWelfares, blank=True, verbose_name="福利待遇")
    label = models.ManyToManyField(PositionLabels, blank=True, verbose_name="职位标签")

    status_choices = ((-1, "DELETED"), (0, "EXPIRED"),(1, "ONLINE"), (2, "UN_PUBLISH"))
    status = models.SmallIntegerField(blank=True, null=True, choices=status_choices, verbose_name="是否有效")
    add_time = models.DateTimeField(blank=True, null=True, verbose_name="新增时间")
    update_time = models.DateTimeField(blank=True, null=True, verbose_name="更新时间")

    class Meta:
        app_label = 'position'
        managed = True
        db_table = 'position_position'
        verbose_name = '招聘职位'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "[" + self.company.name + "]" + self.name if self.company.name else self.name
