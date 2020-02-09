import requests
import datetime
import django
import sys
import os
import logging

from django.db.models import Q

requests.packages.urllib3.disable_warnings()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyroad.settings')
django.setup()

from wuhan2020.models import DXYTimeLine
from public.models import AdministrativeDiv
from public.tools import get_session_request

class CrawlTimeline(object):
    def __init__(self):
        self.start_url = None
        self.counter = {"success": 0, "failed": 0}

    def crawl(self):
        if self.start_url:
            session = get_session_request(self.start_url)
            resp = session.get(self.start_url).json()
            try:
                all_data = resp["data"]
            except:
                raise ValueError("response is not available")
            for data in all_data:
                data_id = data["id"]
                is_exists = DXYTimeLine.objects.filter(id=data_id).exists()
                if not is_exists:
                    #准备字段
                    kwargs = {}
                    kwargs["id"] = data["id"]
                    kwargs["title"] = data["title"]
                    kwargs["source_url"] = data["sourceUrl"]
                    kwargs["source_info"] = data["infoSource"]
                    kwargs["source_summary"] = data["summary"]
                    if data.get("provinceName", None):
                        province = AdministrativeDiv.objects.filter(Q(name=data["provinceName"])|Q(short_name=data["provinceName"]))
                        if province.count() > 0:
                            kwargs["province"] = province[0]
                    kwargs["info_type"] = data["infoType"]
                    kwargs["publish_time"] = datetime.datetime.fromtimestamp(int(data["pubDate"] // 1000))
                    kwargs["create_time"] = datetime.datetime.fromtimestamp(int(data["createTime"] // 1000))
                    kwargs["modify_time"] = datetime.datetime.fromtimestamp(int(data["modifyTime"] // 1000))
                    # 入库
                    try:
                        DXYTimeLine.objects.create(**kwargs)
                        self.counter["success"] += 1
                    except Exception as e:
                        self.counter["failed"] += 1
                        logging.error("data store false! error: %s"%e)


    def run(self):
        logging.warning("spider start")
        self.crawl()
        logging.warning("work finished. success total: %s, fail total: %s"%(self.counter["success"], self.counter["failed"]))

if __name__ == "__main__":
    spider = CrawlTimeline()
    spider.start_url = "https://file1.dxycdn.com/2020/0130/492/3393874921745912795-115.json"
    spider.run()