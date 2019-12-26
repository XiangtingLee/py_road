# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PyroadSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    class IspiderItem(scrapy.Item):
        # define the fields for your item here like:
        # name = scrapy.Field()
        id = scrapy.Field()
        tyc_id = scrapy.Field()
        name = scrapy.Field()
        short_name = scrapy.Field()
        introduce = scrapy.Field()
        certification = scrapy.Field()
        financing = scrapy.Field()
        scale = scrapy.Field()
        industry = scrapy.Field()
        labels = scrapy.Field()
        business_name = scrapy.Field()
        business_credit_code = scrapy.Field()
        business_establish_time = scrapy.Field()
        business_reg_capital = scrapy.Field()
        business_reg_location = scrapy.Field()
        business_legal_person_name = scrapy.Field()
        business_reg_status = scrapy.Field()
        city = scrapy.Field()
        url = scrapy.Field()
        logo = scrapy.Field()
