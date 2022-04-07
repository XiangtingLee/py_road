# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re
import logging
import datetime
from django.db.models import Q
from position.models import *
from public.models import *

logger = logging.getLogger(__name__)


class BaseToolPipeline(object):

    @staticmethod
    def process_simple_foreign_key(model: models, **kwargs):
        """
        处理简单外键，返回符合筛选条件的对象
        :param model:  表模型
        :param kwargs: 筛选条件
        :return:       模型对象
        """
        obj = model.objects.get_or_create(defaults={"add_time": datetime.datetime.now()}, **kwargs)
        return obj[0]

    @staticmethod
    def get_province(name: str, contains=True) -> AdministrativeDiv or None:
        """
        获取省份
        :param name:     省份名称
        :param contains: 是否使用模糊查询
        :return:         省份对象
        """
        if contains:
            return AdministrativeDiv.objects.filter(province__name__contains=name, city__isnull=True).first()
        return AdministrativeDiv.objects.filter(province__name=name, city__isnull=True).first()

    @staticmethod
    def get_city(name: str, contains=True) -> AdministrativeDiv or None:
        """
        获取城市
        :param name:     城市名称
        :param contains: 是否使用模糊查询
        :return:         城市对象
        """
        if contains:
            return AdministrativeDiv.objects.filter(city__name__contains=name, area__isnull=True).first()
        return AdministrativeDiv.objects.filter(city__name=name, area__isnull=True).first()

    @staticmethod
    def get_area(name: str, contains=True) -> AdministrativeDiv or None:
        """
        获取地区
        :param name:     地区名称
        :param contains: 是否使用模糊查询
        :return:         地区对象
        """
        if contains:
            return AdministrativeDiv.objects.filter(area__name__contains=name).first()
        return AdministrativeDiv.objects.filter(area__name=name).first()

    def add_many_to_many_field(self, operate_field, associate_model: models, item_list: list):
        """
        添加多对多字段的关联
        :param operate_field:   要添加关联的字段
        :param associate_model: 关联数据表model
        :param item_list:       关联添加的数据
        :return:                None
        """
        add_list = [self.process_simple_foreign_key(associate_model, name=item) for item in item_list]
        # getattr(operate_obj, operate_field).add(*add_list)      # 如果需要调用字符串表示的方法用getattr(obj, "field")
        operate_field.add(*add_list)
        return


class LaGouWxAppPositionPipeline(BaseToolPipeline):

    def __init__(self):
        self.position_list = set()
        self.storage_count = 0
        self.exist_count = 0
        self.position_cache = {}

    def process_district_foreign_key(self, value: str) -> int:
        city_objs = AdministrativeDiv.objects.filter(short_name=value).order_by("id")
        for obj in city_objs:
            if obj.city and obj.city.id == obj.id:
                return obj.id

    def process_item(self, item, spider):
        job = Position()
        job.id = item["pid"]
        job.name = item["name"]
        job.salary_lower = item["salary_lower"]
        job.salary_upper = item["salary_upper"]
        job.education = self.process_simple_foreign_key(PositionEducation, name=item["education"])
        job.experience = self.process_simple_foreign_key(PositionExperience, name=item["experience"])
        job.nature = self.process_simple_foreign_key(PositionNature, name=item["nature"])
        simple_company_kwargs = {
            "id": item["company_id"],
            "short_name": item["company_short_name"]
        }
        job.company = self.process_simple_foreign_key(Company, **simple_company_kwargs) if item["company_id"] else None
        job.type = self.process_simple_foreign_key(PositionType, name=spider.form["keyword"])
        job.add_time = datetime.datetime.now()
        self.position_cache[item["pid"]] = job

        if len(self.position_cache) == spider.page_size:                    # 缓存达到页面数据数量后开始去重入库
            pids = list(self.position_cache.keys())
            exist_result = Position.objects.in_bulk(pids)                   # 用in_bulk批量查询，减少数据库操作次数
            self.exist_count += len(exist_result)

            for pid in exist_result.keys():                                 # 去重
                logger.info("exist id: " + str(pid))
                del self.position_cache[pid]

            for pid, position in self.position_cache.items():                 # 加入入库队列
                self.position_list.add(position)
                logger.info("storage id: " + str(pid) + " position name: " + position.name)
            self.position_cache.clear()

        if self.position_list.__len__() > spider.per_storage_batch:         # 数据量过大时分批入库
            batch_result = Position.objects.bulk_create(self.position_list)
            self.storage_count += len(batch_result)
            self.position_list.clear()
            logger.debug(f"storage count: {len(batch_result)}")

        return "position id: " + str(item["pid"]) + " position name: " + item["name"]

    def close_spider(self, spider):
        if self.position_list:
            batch_result = Position.objects.bulk_create(self.position_list)
            self.storage_count += len(batch_result)
            logger.debug(f"storage count: {len(batch_result)}")
        else:
            logger.error("no item need to storage")

        logger.debug(f"\ncrawl finished!\n"
                     f"spider_name: {spider.name}\n"
                     f"classify: {spider.classify}\n"
                     f"exist_count: {self.exist_count}\n"
                     f"storage_count: {self.storage_count}")


class LaGouWxAppPositionInfoPipeline(BaseToolPipeline):

    def process_item(self, item, spider):
        job = Position.objects.get(id=item["pid"])
        if not job.add_time:
            job.add_time = job.update_time
        job.update_time = item["update_time"]
        job.street = item["street"]
        job.status = item["status"]
        job.update_time = item["update_time"]
        job.description = item["description"]
        job.district = AdministrativeDiv.objects.filter(
            Q(name__contains=item["district"])
            & Q(city__name__contains=item["city"])
            & Q(province__name__contains=item["province"])).first()
        city = self.get_city(item["city"])
        job.city = city
        if not job.district:
            province = self.get_province(item["province"])
            name = item["district"]
            district = AdministrativeDiv()
            district.name = name
            district.city = city
            district.province = province
            district.add_time = datetime.datetime.now()
            district.save()
            AdministrativeDiv.objects.filter(id=district.id).update(area=district)
            job.district = district
        # 处理商圈所在位置
        job.business_area = self.process_simple_foreign_key(CityBusinessArea, district=job.district,
                                name=item["business_area"]) if job.district and item["business_area"] else None
        # 处理多对多字段：福利、标签
        welfare = re.findall('''[\u4e00-\u9fa5|a-z|A-Z|\d]+''', item["welfare"])
        self.add_many_to_many_field(job.welfare, PositionWelfares, welfare)
        self.add_many_to_many_field(job.label, PositionLabels, item["label"])
        job.save()
        return "update success! id: %s" % item["pid"]


class LaGouWxAppCompanyInfoPipeline(BaseToolPipeline):

    def process_item(self, item, spider):
        company = Company.objects.get(id=item["id"])
        company.short_name = item["short_name"]
        company.city = self.get_city(item["city"])
        company.logo = item["logo"]
        company.introduction = item["introduction"]
        company.financing = self.process_simple_foreign_key(CompanyFinancing, name=item["financing"])
        company.scale = self.process_simple_foreign_key(CompanySize, name=item["scale"])
        # 处理多对多字段
        self.add_many_to_many_field(company.industry, CompanyIndustries, item["industry"])
        company.save()


class LaGouWebCompanyInfoPipeline(BaseToolPipeline):

    def process_item(self, item, spider):
        company = Company.objects.get(id=item["id"])
        financing = self.process_simple_foreign_key(CompanyFinancing, name=item["financing"]) if item["financing"] else None
        size = self.process_simple_foreign_key(CompanySize, name=item["scale"]) if item["scale"] else None
        company.logo = item["logo"]
        company.name = item["name"]
        company.short_name = item["short_name"]
        company.url = item["url"]
        company.introduction = item["introduction"]
        company.profile = item["profile"]
        company.city = self.get_city(item["city"])
        company.size = size
        company.financing = financing
        self.add_many_to_many_field(company.industry, CompanyIndustries, item["industry"])
        self.add_many_to_many_field(company.label, CompanyLabels, item["labels"])

        if item.get("business_name"):
            business_info = BusinessInfo()
            business_info.cid = company.id
            business_info.tyc_id = item["business_tyc_id"]
            business_info.full_name = item["business_name"]
            business_info.credit_code = item["business_credit_code"]
            business_info.establish_time = item["business_establish_time"]
            business_info.reg_capital = item["business_reg_capital"]
            business_info.reg_location = item["business_reg_location"]
            business_info.legal_person_name = item["business_legal_person_name"]
            reg_status = self.process_simple_foreign_key(CompanyRegStatus, name=item["business_reg_status"]) if item["business_reg_status"] else None
            business_info.reg_status = reg_status
            business_info.add_time = datetime.datetime.now()
            business_info.save()
            company.business_info = business_info
        company.save()
        return "update success! company id: " + str(company.id) + " company name: " + company.name


class ProxyZdayePipeLine(object):

    def __init__(self):
        self.proxy_list = list()
        self.storage_count = 0
        self.exist_count = 0

    def process_item(self, item, spider):
        kwargs = item
        kwargs["protocol"] = ProxyPoolProtocol.objects.filter(name=item["protocol"]).first()
        kwargs["type"] = ProxyPoolType.objects.filter(name=item["type"]).first()
        if ProxyPool.objects.filter(address=kwargs["address"], port=kwargs["port"]).first():
            self.exist_count += 1
        else:
            if kwargs["port"] != "0":
                proxy = ProxyPool(**kwargs)
                self.proxy_list.append(proxy)
                self.storage_count += 1
                return "storage success :" + kwargs["address"] + ":" + kwargs["port"]

    def close_spider(self, spider):
        result = ProxyPool.objects.bulk_create(self.proxy_list)
        logger.debug(f"\ncrawl finished!\n"
                     f"spider_name: {spider.name}\n"
                     f"exist_count: {self.exist_count}\n"
                     f"storage_count: {self.storage_count}\n"
                     f"storage_result: {result}")
