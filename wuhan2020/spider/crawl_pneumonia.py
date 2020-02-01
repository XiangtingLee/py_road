import requests
import time
import datetime
import django
import json
import sys
import os
import re
from lxml import etree
import logging

requests.packages.urllib3.disable_warnings()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyroad.settings')
django.setup()

from wuhan2020.models import DXYData
from public.tools import get_session_request

class CrawlPneumonia(object):
    def __init__(self):
        self.start_url = None
        self.modify_time = None
        self.data_element = {
            "getStatisticsService": self.statistics,
            "getIndexRumorList": self.rumor,
            "getTimelineService": self.timeline,
            "getListByCountryTypeService1": self.domestic_province,
            "getAreaStat": self.domestic_area,
            "getListByCountryTypeService2": self.foreign,
        }

    def statistics(self, data:dict):
        modify = data.get("modifyTime", int(time.time()) * 1000)
        self.modify_time = datetime.datetime.fromtimestamp(modify / 1000)
        return json.dumps(data)

    def rumor(self, data:dict):
        return json.dumps(data)

    def timeline(self, data:list):
        return json.dumps(data)

    def domestic_province(self, data:list):
        return json.dumps(data)

    def domestic_area(self, data:list):
        return json.dumps(data)

    def foreign(self, data:list):
        print(data)
        return json.dumps(data)

    def parse_json(self, data:str):
        try:
            search_result = re.search("""try \{ window\..*? =(.*?)\}catch\(e\)\{\}""", data).groups(0)
            search_data = json.loads(search_result[0])
            return search_data
        except:
            return False

    def crawl(self):
        from bs4 import BeautifulSoup
        kwargs = {}
        if self.start_url:
            session = get_session_request(self.start_url)
            resp = session.get(self.start_url)
            soup = BeautifulSoup(resp.content, 'lxml')
            for element, d_obj, in self.data_element.items():

                ele = str(soup.find('script', attrs={'id': '%s'%element}))
                result = self.parse_json(ele)
                if result:
                    kwargs[d_obj.__name__] = d_obj(result)
            kwargs["modify_time"] = self.modify_time
            modify_time_str = self.modify_time.strftime("%Y-%m-%d %H:%M:%S")
            if not DXYData.objects.filter(id=1).exists():
                try:
                    DXYData.objects.create(**kwargs)
                    logging.info("first data store successful! latest : %s"%modify_time_str)
                except Exception as e:
                    logging.error("first data store false! error: %s"%e)
            else:
                last_data_time = DXYData.objects.all()[0]
                if not datetime.datetime.strptime(last_data_time.__str__(), "%Y-%m-%d %H:%M:%S") == self.modify_time:
                    try:
                        DXYData.objects.create(**kwargs)
                        logging.info("data store successful! latest : %s"%modify_time_str)
                    except Exception as e:
                        logging.error("data store false! error: %s"%e)
                else:
                    logging.warning("data already latest! latest : %s"%modify_time_str)
        else:
            raise TypeError("%s.start_url must not be 'None' type."%self.__class__)

    def run(self):
        self.crawl()

if __name__ == "__main__":
    spider = CrawlPneumonia()
    spider.start_url = "http://3g.dxy.cn/newh5/view/pneumonia"
    spider.run()
    # resp = requests.get("https://lab.isaaclin.cn/nCoV/api/overall?latest=0").json()
    # for one in resp["results"]:
    #     print(one["confirmedCount"], datetime.datetime.fromtimestamp(one["updateTime"]/1000))
