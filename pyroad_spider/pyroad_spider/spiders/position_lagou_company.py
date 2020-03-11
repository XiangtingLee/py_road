# -*- coding: utf-8 -*-
import scrapy
import json
import datetime
import requests
from copy import deepcopy

from scrapy.http import Request
# from ..items import PyroadSpiderItem

now = datetime.datetime.now()
now_stamp = int(now.timestamp() * 1000)
now_time = datetime.datetime.strftime(now, "%Y%m%d%H%M%S")

DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    # "Cookie": COOKIE,
    "Host": "www.lagou.com",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/71.0.3578.98 Safari/537.36",
}


class PositionLagouCompanySpider(scrapy.Spider):
    name = 'position_lagou_company'
    allowed_domains = ['lagou.com']
    start_urls = ['https://www.lagou.com/gongsi/%s.html' % i for i in range(7, 17)]
    # start_urls = ['https://www.lagou.com/gongsi/7.html']
    custom_settings = {
        "DEFAULT_REQUEST_HEADERS": DEFAULT_REQUEST_HEADERS,
        'CONCURRENT_REQUESTS': 3,
        'DOWNLOAD_DELAY': 3,
    }

    def __init__(self, *args, **kwargs):
        self.location = kwargs.get('location')
        # COOKIE['index_location_city'] = self.location
        super(PositionLagouCompanySpider, self).__init__(*args, **kwargs)

    @staticmethod
    def update_cookie(url):
        headers = deepcopy(DEFAULT_REQUEST_HEADERS)
        cookie = {
            '_ga': 'GA1.2.292537651.1561974582',
            '_gid': 'GA1.2.623342403.1561974582',
            '_gat': '1',
            'Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6': '{now_stamp}'.format(now_stamp=now_stamp),
            "Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6": "1575814301,1576254082,1576292677",
            'index_location_city': '%E5%85%A8%E5%9B%BD',
            'JSESSIONID': 'ABAAABAAADEAAFI870C1DBC4802EAE5BD89EA3532714610',
            'LGRID': '{now_time}-15c359e9-1e4e-11ea-a69b-5254005c3644'.format(now_time=now_time),
            'LGSID': '{now_time}-a4e44b9c-1e49-11ea-a69b-5254005c3644'.format(now_time=now_time),
            'LGUID': '{now_time}-a82abb0e-19c4-11ea-a696-5254005c3644'.format(now_time=now_time),
            # 'sajssdk_2015_cross_new_user': '1',
            # 'SEARCH_ID': '1d57a392ae7741b0b694775a0d3b859d',
            'user_trace_token': '20190701174940-8bcfa697-9be5-11e9-a4d2-5254005c3644',
            'TG-TRACK-CODE': 'index_navigation',
            # 'X_MIDDLE_TOKEN':'0f7ee5ee733204aef438a3562c4a9f5d',
            'X_HTTP_TOKEN': '12a6b4a6455fb13f3952702651c3da6b3b5c6c2b25',
        }
        resp = requests.get(url, headers=DEFAULT_REQUEST_HEADERS)
        r = resp.cookies.get_dict()
        cookies = deepcopy(cookie)
        cookies.update(r)
        headers["Cookie"] = cookies
        return headers

    def start_requests(self):
        """
        重写start_requests，请求登录页面
        :return:
        """
        for url in self.start_urls:
            # headers = self.update_cookie(url)
            # print(headers["Cookie"]["user_trace_token"])
            # yield Request(url="https://www.lagou.com", meta={'cookiejar': 1, 'url': url},
            #               headers=DEFAULT_REQUEST_HEADERS, callback=self.get_session, dont_filter=True)
            yield Request(url=url, headers=self.update_cookie(url), dont_filter=True, callback=self.parse)

    def get_session(self, response):
        url = response.meta['url']
        return [Request(url=url, callback=self.parse, dont_filter=True)]

    def parse(self, response):
        item = {}
        # print(response.text)
        certification = response.xpath('''//a[@class="aptitude tipsys"]''')
        item["certification"] = True if certification else False
        company_info = response.xpath('''//script[@id="companyInfoData"]/text()''')
        if company_info:
            data = company_info[0].extract()
            info = json.loads(data)
            base_info = info["baseInfo"]
            core_info = info["coreInfo"]
            business_info = info["companyBusinessInfo"]

            item["labels"] = info["labels"]
            item["financing"] = base_info["financeStage"]
            item["scale"] = base_info["companySize"]
            item["industry"] = base_info["industryField"]
            item["city"] = base_info["city"]
            item["id"] = core_info["companyId"]
            item["name"] = core_info["companyName"]
            item["short_name"] = core_info["companyShortName"]
            item["introduce"] = core_info["companyIntroduce"]
            item["url"] = core_info["companyUrl"]
            item["logo"] = core_info["logo"]
            item["tyc_id"] = business_info["tycCompanyId"]
            item["business_name"] = business_info["companyName"]
            item["business_credit_code"] = business_info["creditCode"]
            item["business_establish_time"] = business_info["establishTime"]
            item["business_reg_capital"] = business_info["regCapital"]
            item["business_reg_location"] = business_info["regLocation"]
            item["business_legal_person_name"] = business_info["legalPersonName"]
            item["business_reg_status"] = business_info["regStatus"]
            return item
