# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.org/en/latest/topics/items.html

from scrapy import Item, Field


class PyroadSpiderItem(Item):
    # define the fields for your item here like:
    # name = Field()
    class IspiderItem(Item):
        # define the fields for your item here like:
        # name = Field()
        id = Field()
        tyc_id = Field()
        name = Field()
        short_name = Field()
        introduce = Field()
        certification = Field()
        financing = Field()
        scale = Field()
        industry = Field()
        labels = Field()
        business_name = Field()
        business_credit_code = Field()
        business_establish_time = Field()
        business_reg_capital = Field()
        business_reg_location = Field()
        business_legal_person_name = Field()
        business_reg_status = Field()
        city = Field()
        url = Field()
        logo = Field()


class LaGouWxAppPositionItem(Item):
    pid = Field()
    name = Field()
    salary_lower = Field()
    salary_upper = Field()
    company_id = Field()
    company_short_name = Field()
    education = Field()
    experience = Field()
    city = Field()
    district = Field()
    nature = Field()
    classify = Field()


class LaGouWxAppPositionInfoItem(Item):
    pid = Field()
    status = Field()
    province = Field()
    city = Field()
    district = Field()
    street = Field()
    description = Field()
    update_time = Field()
    welfare = Field()
    label = Field()
    business_area = Field()

class LaGouWebCompanyInfoItem(Item):
    id = Field()
    encrypt_id = Field()
    logo = Field()
    name = Field()
    short_name = Field()
    url = Field()
    city = Field()
    introduction = Field()
    profile = Field()
    financing = Field()
    scale = Field()
    industry = Field()
    # certification = Field()
    labels = Field()
    business_tyc_id = Field()
    business_name = Field()
    business_credit_code = Field()
    business_establish_time = Field()
    business_reg_capital = Field()
    business_reg_location = Field()
    business_legal_person_name = Field()
    business_reg_status = Field()

class LaGouWxAppCompanyInfoItem(Item):
    id = Field()
    short_name = Field()
    city = Field()
    logo = Field()
    introduction = Field()
    financing = Field()
    scale = Field()
    industry = Field()

class ProxyItem(Item):
    protocol = Field()
    address = Field()
    port = Field()
    type = Field()
    add_time = Field()
    update_time = Field()
    is_available = Field()
    is_delete = Field()