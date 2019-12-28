import requests
import time
import os
import sys
import django
import urllib
from queue import Queue
import datetime

requests.packages.urllib3.disable_warnings()
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# print(BASE_DIR)
# sys.path.append(BASE_DIR)
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyroad.settings')
# django.setup()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyroad.settings')
django.setup()

from public.models import AdministrativeDiv, CityBusinessZone
from position.models import *
from position.spider.crawl_company import CrawlCompany
from public.tools import MyThread, ThreadLock


class CrawlPosiion(object):

    def __init__(self):
        self.spider_queue = Queue()
        self.thread_count = 5
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
        self.foreign_fields = {
            "education": "PositionEducation",
            "experience": "PositionExperience",
            "position_nature": "PositionNature",
            "position_type": "PositionType",
        }
        self.cache = self.__cache(self.foreign_fields)

    def __cache(self, foreign_fields):
        '''
        缓存字段数据
        '''
        cache_data = {}
        for key in foreign_fields:
            field = foreign_fields[key]
            cache_data[field] = {}
            obj = eval(field)
            for i in obj.objects.all():
                cache_data[field][i.name] = i
        return cache_data

    def __progress(self, percent, width=50):
        '''进度打印功能
           每次的输入是已经完成总任务的百分之多少
        '''
        show_str = ('正在创建线程,请稍后...[%%-%ds]' % width) % (int(width * percent / 100) * "#")  # 字符串拼接的嵌套使用
        if percent >= 100:
            percent = 100
            show_str = ('创建完成 [%%-%ds]' % width) % (int(width * percent / 100) * "#")
        print('\r%s %d%%' % (show_str, percent), end='')

    def __detect_page(self) -> int:
        '''
        探测数据总页数
        '''
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

    def __get_labels(self, data:str) -> list:
        '''
        分割标签
        '''
        split_str = ['.', ',', '，', '、', ' ', '；', ';', '：']
        data = data.replace('。', '')
        for i in split_str:
            data = data.replace(i, '_')
        return data.split('_')

    def __get_task(self, data):
        '''
        队列任务迭代
        '''
        yield self.store(data)

    def __process_business_zones(self, city, district, zones:list) -> list:
        '''
        处理职位所在商圈
        '''
        zone_ids = []
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
        '''
        处理ManyToMany字段
        '''
        ids = []
        for label in labels:
            try:
                is_exist = obj.objects.get(name=label)
            except models.ObjectDoesNotExist:
                ThreadLock.acquire()
                field_id = obj.objects.create(name=label, add_time=datetime.datetime.now()).id
                ThreadLock.release()
            except:
                ThreadLock.release()
                print("Label '%s' Process Failed! "%label)
                continue
            else:
                field_id = is_exist.id
            ids.append(field_id)
        return ids

    def get_requests_data(self, form_data):
        '''
        请求数据
        '''
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
                data["welfare"] = [] if welfare == "" else self.__get_labels(welfare)
                data["labels"] = item_data["positionLables"]
                data_list.append(data)
            return data_list

    def store(self, data:dict):
        '''
        数据入库
        '''
        for key in self.foreign_fields:
            field = self.foreign_fields[key]
            ThreadLock.acquire()
            key_obj = self.cache[field].get(data[key], None)
            if not key_obj and data[key]:
                try:
                    obj = eval(field)
                    key_obj = obj.objects.create(name=data[key], add_time=datetime.datetime.now())
                    self.cache[field][key_obj.name] = key_obj
                except:
                    ThreadLock.release()
                    print("\033[1;31m\t position %s field %s '%s' Process Failed!\033[0m"%(data["id"], field, data[key]))
            ThreadLock.release()
            data[key] = key_obj
        # 处理公司外键
        cid = data["company"]
        try:
            company = Company.objects.get(id=cid)
        except models.ObjectDoesNotExist:
            company_spider = CrawlCompany()
            store_company = company_spider.run(start_id=cid, count=1)
            if not store_company:
                print("\033[1;31m\t company %s for position %s store false!\033[0m"%(cid, data["id"]))
                del data["company"]
            else:
                company = Company.objects.get(id=cid) if store_company else None
                data["company"] = company
        except:
            print("\033[1;31m\t company %s for position %s not exist!\033[0m"%(cid, data["id"]))
            del data["company"]
        else:
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
            else:
                print("city %s not exits"%data["position_city"])
                del data["position_city"]
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
            else:
                print("district %s-%s not exits"%(data["position_city"], position_district))
                del data["position_district"]
        labels = data.get("labels", None)
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
            print("\033[1;32m\t store position id %s success!\033[0m" % (data["id"]))
        except Exception as e:
            print("\033[1;31m\t store position id %s failed! %s \n\t data:%s\033[0m" % (data["id"], e, data))
            exit(-2)

    def __start_threads(self, threads:list):
        '''
        多线程运行
        '''
        thread_len = threads.__len__()
        print("Thread len: %s"%thread_len)
        range_num = thread_len // self.thread_count
        # 线程切割启动
        for i in range(range_num):
            __start_thread = i * self.thread_count
            __end_thread = (i + 1) * self.thread_count
            # self.__progress(int(__end_thread / range_num * 100))
            print("Process thread No.%s to No.%s..." % (__start_thread, __end_thread))
            for thread in threads[__start_thread : __end_thread]:
                thread.start()
            for thread in threads[__start_thread : __end_thread]:
                thread.join()

            time.sleep(self.thread_delay)
        # 启动剩余线程
        for thread in threads[range_num * 3:]:
            thread.start()
        for thread in threads[range_num * 3:]:
            thread.join()

    def __create_task(self, form_data):

        run = self.get_requests_data(form_data)
        for i in run:
            __task = self.__get_task(i)
            self.spider_queue.put(__task)
    def run(self):
        '''
        入口函数
        '''
        task_threads = []
        queue_threads = []
        page = self.__detect_page()
        print("All page: %s"%page)
        for i in range(1, page + 1):
        # for i in range(1, 21):
            form_data = {
                'first': 'false',
                'pn': i,
                'kd': self.kd,
            }
            thread = MyThread(func=self.__create_task, args=(form_data, ))
            task_threads.append(thread)
        self.__start_threads(task_threads)
        print("Queue ready")
        while not self.spider_queue.empty():
            thread = MyThread(func=next, args=(self.spider_queue.get(), ))
            # thread.setName(str(id))
            queue_threads.append(thread)
        self.__start_threads(queue_threads)


    # def run_one(self, pid):
    #     url = self.url_template.format(cid=pid)
    #     run = self.get_requests_data(pid, url)
    #     self.spider_queue.put(run)
    #     while not self.spider_queue.empty():
    #         next(self.spider_queue.get())

if __name__ == '__main__':
    spider = CrawlPosiion()
    city = "全国"
    spider.kd = "python"
    spider.city = urllib.parse.quote(city)
    spider.run()
    # print(AdministrativeDiv.objects.get(name="北京市").id)
    # print(spider.cache)