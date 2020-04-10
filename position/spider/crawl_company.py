import requests
import time
import datetime
import json
from lxml import etree
import sys
import os
import django
from queue import Queue


requests.packages.urllib3.disable_warnings()
# 这两行很重要，用来寻找项目根目录，os.path.dirname要写多少个根据要运行的python文件到根目录的层数决定
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyroad.settings')
django.setup()

from position.models import *
from public.models import *
from public.tools import MyThread, ThreadLock

class LabelsProcessError(Exception): pass

class CrawlCompany(object):

    def __init__(self):
        self.spider_queue = Queue()
        self.thread_count = 3
        self.thread_delay = 0
        self.foreign_fields = {"scale": "CompanyScale",
                               "financing": "CompanyFinancing",
                               "business_reg_status": "CompanyRegStatus"}
        self.url_template = 'https://www.lagou.com/gongsi/{cid}.html'
        self.headers = {
            'Origin': 'https://www.lagou.com',
            'X-Anit-Forge-Code': '0',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            # 'Referer': 'https://www.lagou.com/jobs/list_python?px=new&city=%E5%85%A8%E5%9B%BD',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'X-Anit-Forge-Token': 'None',
        }
        self.cache = self.__cache(self.foreign_fields)

    def __cache(self, foreign_fields:dict) -> dict:
        cache_data = {}
        for key in foreign_fields:
            field = foreign_fields[key]
            cache_data[field] = {}
            obj = eval(field)
            for i in obj.objects.all():
                cache_data[field][i.name] = i
        return cache_data

    def __process_many_to_many(self, obj:django.db.models.base.ModelBase, labels: list) -> list:
        ids = []
        for label in labels:
            ThreadLock.acquire()
            try:
                field_obj = obj.objects.get(name=label)
            except models.ObjectDoesNotExist:
                field_obj = obj.objects.create(name=label, add_time=datetime.datetime.now())
            except:
                print("Label '%s' Process Failed! "%label)
                continue
            ThreadLock.release()
            ids.append(field_obj)
        return ids

    def get_requests_data(self, cid, url):
        item = {}
        time.sleep(3)
        session_data = requests.session()
        session_data.headers.update(self.headers)
        session_data.get("https://www.lagou.com/gongsi/14.html", verify=False)
        content = session_data.post(url=url)
        result = etree.HTML(content.text)
        company_info = result.xpath("""//script[@id="companyInfoData"]/text()""")
        if company_info:
            info = json.loads(company_info[0])

            certification = result.xpath('''//a[contains(@class, 'tipsys')]//span//text()''')[0]
            item["certification"] = True if len(certification)==4 else False
            base_info = info["baseInfo"]
            core_info = info["coreInfo"]
            business_info = info.get("companyBusinessInfo", False)

            item["label"] = info.get("labels", [])
            item["financing"] = base_info.get("financeStage", None)
            item["scale"] = base_info.get("companySize", None)
            industries = base_info.get("industryField", "")
            item["industry"] = [] if industries == "" else '{},'.format(industries).split(',')[:-1]
            item["city"] = base_info.get("city", None)
            item["id"] = core_info.get("companyId", None)
            item["name"] = core_info.get("companyName", None)
            item["short_name"] = core_info.get("companyShortName", None)
            item["introduce"] = core_info.get("companyIntroduce", None)
            item["url"] = core_info.get("companyUrl", None)
            item["logo"] = core_info.get("logo", None)
            if business_info:
                item["tyc_id"] = business_info.get("tycCompanyId", None)
                item["business_name"] = business_info.get("companyName", None)
                item["business_credit_code"] = business_info.get("creditCode", None)
                item["business_establish_time"] = business_info.get("establishTime", None)
                item["business_reg_capital"] = business_info.get("regCapital", None)
                item["business_reg_location"] = business_info.get("regLocation", None)
                item["business_legal_person_name"] = business_info.get("legalPersonName", None)
                item["business_reg_status"] = business_info.get("regStatus", None)
            yield self.store(item)
        else:
            yield print("\033[1;33m\t company %s not found!\033[0m"%cid)

    def store(self, data: dict):
        for key in self.foreign_fields:
            field = self.foreign_fields[key]
            if key in data:
                ThreadLock.acquire()
                key_obj = self.cache[field].get(data[key], None)
                if not key_obj and data[key]:
                    try:
                        obj = eval(field)
                        key_obj = obj.objects.create(name=data[key], add_time=datetime.datetime.now())
                        self.cache[field][key_obj.name] = key_obj
                        ThreadLock.release()
                    except:
                        ThreadLock.release()
                        print("\033[1;31m\t company %s field %s '%s' Process Failed!\033[0m" % (data["id"], field, data[key]))
                else:
                    ThreadLock.release()
                data[key] = key_obj
            else:
                print("\033[1;33m\t key %s not exists!\033[0m"%key)
        try:
            city = data["city"]
        except KeyError:
            print("\033[1;33m\t key city not exists!\033[0m")
        else:
            del data["city"]
            if city != '':
                city_ins = AdministrativeDiv.objects.filter(short_name=city)
                if city_ins:
                    city_id = city_ins[0].id
                    data["city_id"] = city_id
        data['warehouse_time'] = datetime.datetime.now()
        labels = data.get("label", None)
        industry = data.get("industry", None)
        del data["label"]
        del data["industry"]
        try:
            result = Company.objects.create(**data)
            if labels:
                labels_id = self.__process_many_to_many(CompanyLabels, labels)
                result.label.set(labels_id)
            if industry:
                industry_id = self.__process_many_to_many(CompanyIndustries, industry)
                result.industry.set(industry_id)
            print("\033[1;32m\t store company id %s success!\033[0m"%(data["id"]))
        except Exception as e:
            if "PRIMARY" not in str(e):
                print("\033[1;31m\t store company id %s failed! %s\033[0m"%(data["id"], e))
                # print("\t%s"%data)

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


    def run(self, start_id, count):
        threads = []
        for cid in range(start_id, start_id + count):
            url = self.url_template.format(cid=cid)
            run = self.get_requests_data(cid, url)
            self.spider_queue.put(run)
        while not self.spider_queue.empty():
            thread = MyThread(func=next, args=(self.spider_queue.get(), ))
            thread.setName(str(id))
            threads.append(thread)
        self.__start_threads(threads)
        return True


if __name__ == '__main__':
    spider = CrawlCompany()
    spider.thread_count = 5
    spider.run(start_id=1, count=10)
