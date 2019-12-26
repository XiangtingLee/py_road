import requests
import time
import os
import sys
import django
import urllib
from queue import Queue
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyroad.settings')
django.setup()
requests.packages.urllib3.disable_warnings()

from public.models import *
from position.models import *
from position.spider.company import CrawlCompany
from public.tools import MyThread, ThreadLock

class CrawlPosiion(object):

    def __init__(self):
        self.spider_queue = Queue()
        self.thread_count = 3
        self.thread_delay = 0
        self.city = "%E5%85%A8%E5%9B%BD"
        self.kd = "python"
        self.data_url = 'https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false&city={}'
        self.headers = {
            'Origin': 'https://www.lagou.com',
            'X-Anit-Forge-Code': '0',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Referer': 'https://www.lagou.com/jobs/list_python?px=new&city=%E5%85%A8%E5%9B%BD',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'X-Anit-Forge-Token': 'None',
        }
        self.foreignkey = {
            "education": "PositionEducation",
            "experience": "PositionExperience",
            "position_nature": "PositionNature",
            "position_type": "PositionType",
        }
        self.cache = self.__cache(self.foreignkey)

    def __cache(self, foreign_fields):
        cache_data = {}
        for key in foreign_fields:
            field = foreign_fields[key]
            cache_data[field] = {}
            obj = eval(field)
            for i in obj.objects.all():
                cache_data[field][i.name] = i
        return cache_data

    def __detect_page(self) -> int:
        form_data = {
            'first': 'false',
            'pn': '1',
            'kd': 'python',
        }
        session_data = requests.session()
        session_data.headers.update(self.headers)
        session_data.get("https://www.lagou.com/jobs/list_Python?px=new&city=%s"%self.city) #北京
        content = session_data.post(url=self.data_url.format(self.city), data=form_data)
        result = content.json()
        total = result["content"]["positionResult"]["totalCount"]
        page_size = result["content"]["pageSize"]
        page = int(total) // int(page_size) + 1
        return int(page)

    def __process_business_zones(self, city, district, zones:list) -> list:
        zone_ids = []
        # 循环处理所在商圈
        for zone in zones:
            kwargs = {"name": zone}
            if isinstance(city, AdministrativeDiv):
                kwargs["city"] = city
            if isinstance(district, AdministrativeDiv):
                kwargs["area"] = district
            try:
                zone_ins = CityBusinessZone.objects.get(**kwargs)
                zone_id = zone_ins.id if zone_ins else None
            except models.ObjectDoesNotExist:
                kwargs["add_time"] = datetime.datetime.now()
                zone_id = CityBusinessZone.objects.create(**kwargs).id
            if zone_id:
                zone_ids.append(zone_id)
        return zone_ids

    def __process_many_to_many(self, obj:django.db.models.base.ModelBase, labels: list) -> list:
        ids = []
        ThreadLock.acquire()
        for label in labels:
            try:
                is_exist = obj.objects.get(name=label)
            except models.ObjectDoesNotExist:
                field_id = obj.objects.create(name=label, add_time=datetime.datetime.now()).id
            except:
                print("Label '%s' Process Failed! "%label)
                continue
            else:
                field_id = is_exist.id
            ids.append(field_id)
        ThreadLock.release()
        return ids

    def get_requests_data(self, form_data):
        time.sleep(3)
        session_data = requests.session()
        session_data.headers.update(self.headers)
        session_data.get("https://www.lagou.com/jobs/list_Python?px=new&city=%s"%self.city)
        content = session_data.post(url=self.data_url.format(self.city), data=form_data)
        result = content.json()
        try:
            result_data_list = result['content']['positionResult']['result']
        except:
            return False
        else:
            data_list = []
            for item_data in result_data_list:
                data = {}
                data["company"] = item_data["companyId"]
                data["id"] = item_data["positionId"]
                data["position_name"] = item_data["positionName"]
                data["position_type"] = "Python"
                data["position_nature"] = item_data["jobNature"]
                data["position_city"] = item_data["city"]
                data["position_district"] = item_data["district"]
                data["position_business_zones"] = item_data["businessZones"]
                data["education"] = item_data["education"]
                data["experience"] = item_data["workYear"]
                data["salary_lower"] = int(item_data["salary"].lower().replace('-','').split('k')[0])
                data["salary_upper"] = int(item_data["salary"].lower().replace('-','').split('k')[1])
                data["welfare"] = item_data["positionAdvantage"]
                welfare = item_data.get("positionAdvantage", "")
                data["welfare"] = [] if welfare == "" else '{},'.format(welfare).split(',')[:-1]
                data["labels"] = item_data["positionLables"]
                data_list.append(data)
            return data_list

    def __get_task(self, data):
        yield self.store(data)

    def store(self, data:dict):
        if data:
            for key in self.foreignkey:
                field = self.foreignkey[key]
                key_obj = self.cache[field].get(data[key], None)
                if not key_obj:
                    ThreadLock.acquire()
                    obj = eval(self.foreignkey[key])
                    key_obj = obj.objects.create(name=data[key], add_time=datetime.datetime.now())
                    self.cache[field][key_obj.name] = key_obj
                    ThreadLock.release()
                data[key] = key_obj
            # 处理公司外键
            cid = data["company"]
            try:
                company = Company.objects.get(id=cid)
            except:
                company_spider = CrawlCompany()
                # todo 处理公司爬虫的返回类型
                store_company = company_spider.run(start_id=cid, count=1)
                company = Company.objects.get(id=cid) if store_company else None
            data["company"] = company
            # try:
            position_city = data["position_city"]
            # except KeyError:
                # print("key 'position_city' not exists!")
            # else:
            if position_city != '':
                city_ins = AdministrativeDiv.objects.filter(short_name=position_city)
                if city_ins:
                    city_obj = city_ins[0]
                    data["position_city"] = city_obj
            # try:
            position_district = data["position_district"]
            # except KeyError:
            #     print("key 'position_district' not exists!")
            # else:
            if position_district != '':
                city_ins = AdministrativeDiv.objects.filter(short_name=position_district)
                if city_ins:
                    city_obj = city_ins[0]
                    data["position_district"] = city_obj
            labels = data.get("label", None)
            welfare = data.get("welfare", None)
            position_business_zones = data.get("position_business_zones", None)
            del data["labels"]
            del data["welfare"]
            del data["position_business_zones"]
            data['warehouse_time'] = datetime.datetime.now()
            try:
                # create Position obj
                position_obj = Position.objects.create(**data)
                if labels:
                    labels_id = self.__process_many_to_many(PositionLabels, labels)
                    position_obj.label.set(labels_id)
                if welfare:
                    welfare_id = self.__process_many_to_many(PositionWelfares, welfare)
                    position_obj.welfare.set(welfare_id)
                # process business zones
                if position_business_zones:
                    zone_ids = self.__process_business_zones(data["position_city"], data["position_district"],
                                                             position_business_zones)
                    position_obj.position_business_zones.set(zone_ids)
                print("store position id %s success!" % (data["id"]))
            except Exception as e:
                print("store position id %s failed! %s" % (data["id"], e))

    def __start_threads(self, threads:list):
        thread_len = threads.__len__()
        range_num = thread_len // self.thread_count
        # 线程切割启动
        for i in range(range_num):
            for thread in threads[i * self.thread_count : (i + 1) * self.thread_count]:
                thread.start()
            for thread in threads[i * self.thread_count : (i + 1) * self.thread_count]:
                thread.join()
            time.sleep(self.thread_delay)
        # 启动剩余线程
        for thread in threads[range_num * 3:]:
            thread.start()
        for thread in threads[range_num * 3:]:
            thread.join()


    def run(self):
        threads = []
        page = self.__detect_page()
        print("All page: %s"%page)
        for page in range(1, page + 1):
        # for page in range(1, 2):
            form_data = {
                'first': 'false',
                'pn': page,
                'kd': self.kd,
            }
            run = self.get_requests_data(form_data)
            for i in run:
                __task = self.__get_task(i)
                self.spider_queue.put(__task)
        print("Queue ready")
        while not self.spider_queue.empty():
            thread = MyThread(func=next, args=(self.spider_queue.get(), ))
            thread.setName(str(id))
            threads.append(thread)
        self.__start_threads(threads)


if __name__ == '__main__':
    spider = CrawlPosiion()
    city = "全国"
    spider.kd = "python"
    spider.city = urllib.parse.quote(city)
    spider.run()
    # print(AdministrativeDiv.objects.get(name="北京市").id)
    # print(spider.cache)