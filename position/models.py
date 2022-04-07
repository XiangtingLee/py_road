from django.db import models
from public.models import AdministrativeDiv, CityBusinessArea


# Create your models here.
class CompanySize(models.Model):
    name = models.CharField(max_length=20, verbose_name="规模名称")
    add_time = models.DateTimeField(verbose_name="新增时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_effective = models.BooleanField(default=True, verbose_name="是否有效")

    class Meta:
        managed = True
        db_table = 'position_company_size'
        verbose_name = '公司规模'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class CompanyRegStatus(models.Model):
    name = models.CharField(max_length=50, verbose_name="状态名称")
    add_time = models.DateTimeField(verbose_name="新增时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_effective = models.BooleanField(default=True, verbose_name="是否有效")

    class Meta:
        managed = True
        db_table = 'position_company_reg_status'
        verbose_name = '公司经营状态'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class CompanyFinancing(models.Model):
    name = models.CharField(max_length=20, verbose_name="阶段名称")
    add_time = models.DateTimeField(verbose_name="新增时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_effective = models.BooleanField(default=True, verbose_name="是否有效")

    class Meta:
        managed = True
        db_table = 'position_company_financing'
        verbose_name = '公司融资阶段'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class CompanyIndustries(models.Model):
    name = models.CharField(max_length=50, verbose_name="行业名称")
    add_time = models.DateTimeField(verbose_name="新增时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_effective = models.BooleanField(default=True, verbose_name="是否有效")

    class Meta:
        managed = True
        db_table = 'position_company_industries'
        verbose_name = '公司所属行业'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class CompanyLabels(models.Model):
    name = models.CharField(max_length=20, verbose_name="标签名称")
    add_time = models.DateTimeField(verbose_name="新增时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_effective = models.BooleanField(default=True, verbose_name="是否有效")

    class Meta:
        managed = True
        db_table = 'position_company_labels'
        verbose_name = '公司标签'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class PositionType(models.Model):
    name = models.CharField(max_length=20, verbose_name="类型名称")
    add_time = models.DateTimeField(verbose_name="新增时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_effective = models.BooleanField(default=True, verbose_name="是否有效")

    class Meta:
        managed = True
        db_table = 'position_position_type'
        verbose_name = '职位类型'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class PositionNature(models.Model):
    name = models.CharField(max_length=20, verbose_name="类型名称")
    add_time = models.DateTimeField(verbose_name="新增时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_effective = models.BooleanField(default=True, verbose_name="是否有效")

    class Meta:
        managed = True
        db_table = 'position_position_nature'
        verbose_name = '职位性质'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class PositionEducation(models.Model):
    name = models.CharField(max_length=10, verbose_name="学历要求")
    add_time = models.DateTimeField(verbose_name="新增时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_effective = models.BooleanField(default=True, verbose_name="是否有效")

    class Meta:
        managed = True
        db_table = 'position_position_education'
        verbose_name = '学历要求'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class PositionExperience(models.Model):
    name = models.CharField(max_length=10, verbose_name="经验要求")
    add_time = models.DateTimeField(verbose_name="新增时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_effective = models.BooleanField(default=True, verbose_name="是否有效")

    class Meta:
        managed = True
        db_table = 'position_position_experience'
        verbose_name = '经验要求'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class PositionWelfares(models.Model):
    name = models.CharField(max_length=50, verbose_name="福利名称")
    add_time = models.DateTimeField(verbose_name="新增时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_effective = models.BooleanField(default=True, verbose_name="是否有效")

    class Meta:
        managed = True
        db_table = 'position_position_welfares'
        verbose_name = '职位福利'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class PositionLabels(models.Model):
    name = models.CharField(max_length=20, verbose_name="标签名称")
    add_time = models.DateTimeField(verbose_name="新增时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_effective = models.BooleanField(default=True, verbose_name="是否有效")

    class Meta:
        managed = True
        db_table = 'position_position_labels'
        verbose_name = '职位标签'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class BusinessInfo(models.Model):
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
        managed = True
        db_table = 'position_company_business'
        verbose_name = '公司工商信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.id) if not self.full_name else self.full_name


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
    business_info = models.ForeignKey(BusinessInfo, on_delete=models.CASCADE, blank=True, null=True,
                                      verbose_name="工商信息")
    is_effective = models.BooleanField(blank=True, default=True, verbose_name="是否有效")
    add_time = models.DateTimeField(blank=True, null=True, verbose_name="新增时间")
    update_time = models.DateTimeField(blank=True, null=True, auto_now=True, verbose_name="更新时间")

    class Meta:
        managed = True
        db_table = 'position_company'
        verbose_name = '招聘公司'
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.id) if not self.name else self.name


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
        managed = True
        db_table = 'position_position'
        verbose_name = '招聘职位'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "[" + self.company.name + "]" + self.name if self.company.name else self.name
