# -*- coding: utf-8 -*-
import scrapy


class PositionLagouPositionSpider(scrapy.Spider):
    name = 'position_lagou_position'
    allowed_domains = ['lagou.com']
    start_urls = ['http://lagou.com/']

    def parse(self, response):
        pass
